#!/usr/bin/env python
# coding: utf-8
# ******************************************************************************
# Copyright 2020 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
"""
Training script for ImageNet models.
"""

import os
import argparse

import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds


import tf_keras as keras
from tf_keras.callbacks import LearningRateScheduler
from tf_keras import Sequential
from tf_keras.optimizers import SGD
from tf_keras.optimizers.legacy import Adam
from tf_keras.layers import Input
from tf_keras.models import clone_model

import akida
from cnn2snn import convert

from .preprocessing import preprocess_image, DATA_AUGMENTATION
from ..training import (get_training_parser, freeze_model_before, print_history_stats, RestoreBest,
                        save_model)
from ..extract import extract_samples
from ..param_scheduler import get_cosine_lr_scheduler
from ..optimizers import LAMB
from ..utils import get_tensorboard_callback
from ..model_io import load_model


def get_imagenet_dataset(data_path, training, image_size, batch_size, data_aug=True, one_hot=False):
    """ Loads ImageNet 2012 dataset and builds a tf.dataset out of it.

    Args:
        data_path (str): path to the folder containing ImageNet tar files
        training (bool): True to retrieve training data, False for validation
        image_size (tuple): desired image size
        batch_size (int): the batch size
        data_aug (bool, optional): True to apply data augmentation (only train). Defaults to True.
        one_hot (bool, optional): whether to one hot labels or not. Defaults to False.

    Returns:
        tf.dataset, int: the requested dataset (train or validation) and the
        corresponding steps
    """
    # Build the dataset
    write_dir = os.path.join(data_path, 'tfds')

    download_and_prepare_kwargs = {
        'download_dir': os.path.join(write_dir, 'downloaded'),
        'download_config': tfds.download.DownloadConfig(manual_dir=data_path)
    }

    split = 'train' if training else 'validation'

    dataset, infos = tfds.load(
        'imagenet2012',
        data_dir=os.path.join(write_dir, 'data'),
        split=split,
        shuffle_files=training,
        download=True,
        as_supervised=True,
        download_and_prepare_kwargs=download_and_prepare_kwargs,
        with_info=True)

    if training:
        dataset = dataset.shuffle(10000, reshuffle_each_iteration=True).repeat()

    data_aug = DATA_AUGMENTATION if data_aug else None
    dataset = dataset.map(lambda image, label: (preprocess_image(
        image, image_size, training, data_aug), label))

    # One hot encode labels if requested
    if one_hot:
        num_classes = infos.features["label"].num_classes
        dataset = dataset.map(lambda image, label: (image, tf.one_hot(label, num_classes)))

    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(1)

    # The following will silence a Tensorflow warning on auto shard policy
    options = tf.data.Options()
    options.experimental_distribute.auto_shard_policy = tf.data.experimental.AutoShardPolicy.DATA
    dataset = dataset.with_options(options)

    return dataset, infos.splits[split].num_examples / batch_size


def compile_model(model, optimizer="SGD"):
    """ Compiles the model.

    Args:
        model (keras.Model): the model to compile
        optimizer (str, optional): the optimizer to use. Defaults to "SGD".

    Returns:
        bool: True if labels should be one-hot encoded, False if not.
    """

    def _get_optim(optim_str):
        optim_str_low = optim_str.lower()
        if optim_str_low == "sgd":
            return SGD(momentum=0.9)
        elif optim_str_low == "adam":
            return Adam(epsilon=1e-8)
        elif optim_str_low == "lamb":
            return LAMB(epsilon=1e-8, weight_decay_rate=2e-2)
        else:
            raise ValueError(f"Unknown optimizer {optim_str}. "
                             "Please choose one of these options: {SGD, ADAM, LAMB}")

    model.compile(optimizer=_get_optim(optimizer),
                  loss=keras.losses.CategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy', 'top_k_categorical_accuracy'])
    return True


def evaluate(model, val_dataset, batch_size, num_samples, val_steps):
    """ Evaluates model performances.

    Args:
        model (keras.Model or akida.Model): the model to compile evaluate
        val_dataset (tf.dataset): validation dataset
        batch_size (int): the batch size
        num_samples (int): number of samples to use for Akida
        val_steps (int): validation steps
    """
    if isinstance(model, akida.Model):
        correct_preds = 0
        cur_samples = 0
        total_samples = val_steps * batch_size
        if num_samples <= 0:
            num_samples = total_samples
        else:
            num_samples = min(num_samples, total_samples)
        it = val_dataset.as_numpy_iterator()

        print(f"Processing {num_samples} samples.")
        if num_samples > batch_size:
            n_batches = num_samples // batch_size
            if n_batches > 5:
                log_samples = (n_batches // 5) * batch_size
            else:
                log_samples = batch_size
            print(f"Logging every {log_samples} samples.")
        else:
            log_samples = num_samples
        while cur_samples < num_samples:
            x, y = next(it)
            y_ak = model.predict_classes(x.astype(np.uint8))
            correct_preds += np.sum(y_ak == np.argmax(y, -1))
            cur_samples += y_ak.shape[0]
            if cur_samples % log_samples == 0 and cur_samples < num_samples:
                # Log current accuracy
                accuracy = correct_preds / cur_samples
                print(f"Accuracy after {cur_samples}: {accuracy}")
        accuracy = correct_preds / cur_samples
        print(f"Accuracy after {cur_samples}: {accuracy}")
    else:
        history = model.evaluate(val_dataset, steps=val_steps)
        print(history)


def rescale(base_model, input_size):
    """ Rescales the model by changing its input size.

    Args:
        base_model (keras.Model): the model to rescale
        input_size (tuple): desired model input size

    Returns:
        keras.Model: the rescaled model
    """
    assert len(input_size) <= 2, f"Cannot rescale to {input_size}, only 2D array are supported."
    if len(input_size) == 1:
        input_size = (input_size[0], input_size[0])
    else:
        input_size = tuple(input_size)

    # Create the desired input
    input_shape = (input_size[0], input_size[1], base_model.input.shape[-1])
    new_input = Input(input_shape)

    # Workaround to force the input shape update that is not working for
    # functional models: the input_tensors parameter is ignored as described in
    # https://github.com/tensorflow/tensorflow/issues/40617.
    if not isinstance(base_model, Sequential):
        base_model.layers[0]._batch_input_shape = (None, input_size[0], input_size[1],
                                                   base_model.input.shape[-1])
        new_input = None

    # Clone the model and replace input layer
    clone = clone_model(base_model, input_tensors=new_input)
    clone.set_weights(base_model.get_weights())
    return clone


def train(model,
          train_dataset,
          train_steps,
          val_dataset,
          val_steps,
          out_dir,
          num_epochs,
          tune=False,
          learning_rate=1e-1,
          initial_epoch=0,
          lr_policy='exp_decay'):
    """ Trains the model

    Args:
        model (keras.Model): the model to train
        train_dataset (tf.dataset): training dataset
        train_steps (int): train steps
        val_dataset (tf.dataset): validation dataset
        val_steps (int): validation steps
        out_dir (str): parent directory for logs folder
        num_epochs (int): the number of epochs
        tune (bool, optional): enable tuning (lower learning rate). Defaults to
          False.
        learning_rate (float, optional): the learning rate. Defaults to 1e-1.
        initial_epoch (int, optional): epoch at which to start training.
          Defaults to 0.
        lr_policy (str, optional): defines the learning rate policy to adopt. Values in
            ['exp_decay', 'cosine_decay', 'cosine_sched'] for exponential decay, cosine decay and
            cosine oscillation respectively. Defaults to 'exp_decay'.
    """
    # 1. Define training callbacks
    callbacks = []

    # 1.1 Learning rate scheduler
    if lr_policy == 'exp_decay':
        LR_START = learning_rate
        LR_END = 1e-4
        # number of epochs you first keep the learning rate constant
        LR_EPOCH_CONSTANT = 10
        # Modify default values for fine-tuning
        if tune:
            LR_START = 1e-4
            LR_END = 1e-8
            LR_EPOCH_CONSTANT = 2

        if LR_EPOCH_CONSTANT >= num_epochs:
            lr_decay = LR_END / LR_START
        else:
            lr_decay = (LR_END / LR_START)**(1. / (num_epochs - LR_EPOCH_CONSTANT))

        # This function keeps the learning rate at LR_START for the first N epochs
        # and decreases it exponentially after that.
        def agg_lr_scheduler(epoch):
            if epoch < LR_EPOCH_CONSTANT:
                return LR_START
            return LR_START * lr_decay**(epoch - (LR_EPOCH_CONSTANT - 1))

        lr_scheduler = LearningRateScheduler(agg_lr_scheduler)
    elif lr_policy == 'cosine_decay':
        LR_START = learning_rate
        if tune:
            LR_EPOCH_CONSTANT = 2  # number of epochs you first keep the learning rate constant
            LR_MIN = 1e-8
        else:
            LR_EPOCH_CONSTANT = 5  # number of epochs you first keep the learning rate constant
            LR_MIN = 1e-6
        # Make sure to start with a learning rate higher than LR_MIN
        LR_MIN = LR_MIN if LR_START > LR_MIN else 0.1 * LR_START

        # If the number of epochs is too small, dont use WARMUP_LR
        if num_epochs < LR_EPOCH_CONSTANT:
            LR_EPOCH_CONSTANT = 0

        # This function keeps the learning rate at LR_START for the first N epochs and decreases it
        # following
        # https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/schedules/CosineDecay
        def cos_lr_scheduler(epoch):
            if epoch < LR_EPOCH_CONSTANT:
                return LR_START
            step = min(epoch, num_epochs) - LR_EPOCH_CONSTANT
            cosine_decay = 0.5 * (1 + np.cos(np.pi * step / (num_epochs - LR_EPOCH_CONSTANT)))
            decayed = (1 - LR_MIN) * cosine_decay + LR_MIN
            return LR_START * decayed
        lr_scheduler = LearningRateScheduler(cos_lr_scheduler)
    elif lr_policy == 'cosine_sched':
        lr_scheduler = get_cosine_lr_scheduler(learning_rate, num_epochs * train_steps)
    else:
        raise ValueError(f"Unsupported learning rate policy '{lr_policy}'.")
    callbacks.append(lr_scheduler)

    # 1.2 Model checkpoints (save best model and retrieve it when training is complete)
    restore_model = RestoreBest(model)
    callbacks.append(restore_model)

    # 1.3 Tensorboard logs
    tensorboard = get_tensorboard_callback(out_dir, prefix='imagenet')
    callbacks.append(tensorboard)

    # 2. Train
    history = model.fit(train_dataset,
                        steps_per_epoch=train_steps,
                        epochs=num_epochs,
                        callbacks=callbacks,
                        validation_data=val_dataset,
                        validation_steps=val_steps,
                        initial_epoch=initial_epoch)
    print_history_stats(history)


def main():
    """ Entry point for script and CLI usage.

    Note: Download the ImageNet training and validation dataset tar files from
    [ImageNetwebsite](https://image-net.org/index.php)
    """
    global_parser = argparse.ArgumentParser(add_help=False)
    global_parser.add_argument(
        "-d",
        "--data",
        type=str,
        required=True,
        help="The directory containing the ImageNet data.")
    global_parser.add_argument("-o",
                               "--out_dir",
                               type=str,
                               default='./logs',
                               help="The output directory (logs, checkpoints).")

    parsers = get_training_parser(batch_size=128,
                                  extract=True,
                                  freeze_before=True,
                                  tune=True,
                                  global_parser=global_parser)

    train_parser = parsers[1]
    train_parser.add_argument("-lr",
                              "--learning_rate",
                              type=float,
                              default=1e-1,
                              help="Learning rate start value.")
    train_parser.add_argument("-ie",
                              "--initial_epoch",
                              type=int,
                              default=0,
                              help="Epoch at which to start training.")
    train_parser.add_argument("--optim", type=str, default="SGD",
                              help="Optimizer to use. Defaults to %(default)s.")
    train_parser.add_argument("--data_aug", action='store_true', help="Enables custom DA.")
    train_parser.add_argument("--lr_policy",
                              default='exp_decay',
                              choices=['exp_decay', 'cosine_decay', 'cosine_sched'],
                              help="Defines the learning rate scheduling. Values in "
                                   "['exp_decay', 'cosine_decay', 'cosine_sched'] which corresponds"
                                   " to exponential decay, cosine decay and cosine oscillation "
                                   "respectively.")

    tune_parser = parsers[2]
    tune_parser.add_argument("-ie",
                             "--initial_epoch",
                             type=int,
                             default=0,
                             help="Epoch at which to start training.")
    tune_parser.add_argument("-lr",
                             "--learning_rate",
                             type=float,
                             default=6e-5,
                             help="Learning rate start value.")
    tune_parser.add_argument("--data_aug",
                             action='store_true',
                             help="Enables custom DA.")
    tune_parser.add_argument("--optim",
                             type=str,
                             default="SGD",
                             help="Optimizer to use. Defaults to %(default)s.")
    tune_parser.add_argument("--lr_policy",
                             default='exp_decay',
                             choices=['exp_decay', 'cosine_decay', 'cosine_sched'],
                             help="Defines the learning rate scheduling. Values in "
                                  "['exp_decay', 'cosine_decay', 'cosine_sched'] which corresponds "
                                  "to exponential decay, cosine decay and cosine oscillation "
                                  "respectively.")

    eval_parser = parsers[3]
    eval_parser.add_argument("-ns",
                             "--num_samples",
                             type=int,
                             default=-1,
                             help="Number of samples to use (for Akida)")

    subparsers = parsers[-1]
    rescale_parser = subparsers.add_parser("rescale", help="Rescale a model.")
    rescale_parser.add_argument("-m",
                                "--model",
                                type=str,
                                required=True,
                                help="Model to load")
    rescale_parser.add_argument("-i",
                                "--input_size",
                                type=int,
                                nargs='+',
                                required=True,
                                help="The input image size")
    rescale_parser.add_argument("-s",
                                "--savemodel",
                                type=str,
                                default=None,
                                help="Save model with the specified name")

    args = parsers[0].parse_args()

    # Load the source model
    model = load_model(args.model)
    im_size = model.input_shape[1:3]

    # Freeze the model
    if "freeze_before" in args:
        freeze_model_before(model, args.freeze_before)

    # Compile model
    one_hot = compile_model(model, optimizer=getattr(args, "optim", "SGD"))

    # Load validation data
    if args.action in ['train', 'tune', 'eval']:
        val_ds, val_steps = get_imagenet_dataset(args.data, False, im_size,
                                                 args.batch_size, data_aug=False, one_hot=one_hot)
    # Load training data
    if args.action in ['train', 'tune', 'extract']:
        data_aug = args.data_aug if args.action in ['train', 'tune'] else False
        train_ds, train_steps = get_imagenet_dataset(args.data, True, im_size,
                                                     args.batch_size, data_aug, one_hot=one_hot)

    # Disable QuantizeML assertions
    os.environ["ASSERT_ENABLED"] = "0"

    # Train model
    if args.action in ['train', 'tune']:
        tune = args.action == 'tune'

        learning_rate = args.learning_rate
        if args.lr_policy == 'cosine_decay':
            # Tune learning rate following https://arxiv.org/pdf/2012.12877.pdf
            learning_rate *= args.batch_size / 512

        train(model,
              train_ds,
              train_steps,
              val_ds,
              val_steps,
              args.out_dir,
              args.epochs,
              tune=tune,
              learning_rate=learning_rate,
              initial_epoch=args.initial_epoch,
              lr_policy=args.lr_policy)
        save_model(model, args.model, args.savemodel, args.action)

    elif args.action == 'eval':
        # Evaluate model accuracy
        if args.akida:
            model = convert(model)
        evaluate(model, val_ds, args.batch_size, args.num_samples, val_steps)

    elif args.action == 'rescale':
        # Rescale model
        m = rescale(model, args.input_size)
        save_model(m, args.model, args.savemodel, args.action)

    elif args.action == 'extract':
        # Extract samples from dataset
        extract_samples(args.savefile, train_ds, args.batch_size)


if __name__ == "__main__":
    main()
