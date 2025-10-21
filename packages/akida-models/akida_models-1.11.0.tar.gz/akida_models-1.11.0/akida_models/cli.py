#!/usr/bin/env python
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
akida_models main command-line interface

This package entry-point allows Keras models of Akida model zoo to be instantiated and saved at a
specified location.

"""

import argparse
import os
import sys
import onnx
import numpy as np

from .utk_face.model_vgg import vgg_utk_face
from .kws.model_ds_cnn import ds_cnn_kws
from .modelnet40.model_pointnet_plus import pointnet_plus_modelnet40
from .imagenet.model_mobilenet import mobilenet_imagenet
from .imagenet.model_akidanet import akidanet_imagenet
from .imagenet.model_akidanet_edge import akidanet_edge_imagenet
from .imagenet.model_akidanet18 import akidanet18_imagenet
from .detection.model_yolo import yolo_base
from .dvs.model_convtiny import convtiny_dvs
from .mnist.model_gxnor import gxnor_mnist
from .portrait128.model_akida_unet import akida_unet_portrait128
from .centernet.model_centernet import centernet_base
from .sparsity import compute_sparsity
from .model_io import load_weights, save_weights, load_model
from .unfuse_sepconv_layers import unfuse_sepconv2d
from .tenn_spatiotemporal import (tenn_spatiotemporal_dvs128, tenn_spatiotemporal_eye,
                                  tenn_spatiotemporal_jester)


def save_model_weights(model_path, weights_path):
    """ CLI entry point to save the model weights in an npz file.

    Args:
        model_path (str): Path to the model to extract the weights from.
        weights_path (str): Path to save the npz file.
            Defaults to <model_path>.npz.
    """
    # Build name for weights file
    if weights_path is None:
        model_name = os.path.splitext(model_path)[0]
        weights_path = f"{model_name}.npz"

    # Load the model and save its weights
    model = load_model(model_path)
    save_weights(model, weights_path)
    print(f"Saved model weights to {weights_path}.")


def load_model_weights(model_path, weights_path):
    """ CLI entry point to apply weights to a model from an npz file.

    Args:
        model_path (str): Path to the model on which apply the weights.
        weights_path (str): Path to load the npz file.
    """
    # Update the model weights with the npz file
    model = load_model(model_path)
    load_weights(model, weights_path)
    model.save(model_path, include_optimizer=False)
    print(f"Saved model with new weights to {model_path}.")


def add_common_args(parser, default_classes, default_alpha=None, default_img_size=None,
                    bw_required=None):
    """ Add commons arguments to the given parser.

    Args:
        parser (argparse.ArgumentParser): parser to add args to.
        default_classes (int): default number of classes.
        default_alpha (float, optional): default alpha. Defaults to None.
        default_img_size (int, optional): default image size. Defaults to None.
        bw_required (bool, optional): when base_weights is required. Defaults to None.
    """
    parser.add_argument("-c", "--classes", type=int, default=default_classes,
                        help="The number of classes, by default %(default)s.")
    if default_img_size is not None:
        img_sizes = [32, 64, 96, 128, 160, 192, 224]
        parser.add_argument("-i", "--image_size", type=int,
                            default=default_img_size, choices=img_sizes,
                            help="The square input image size, by default %(default)s.")
    if default_alpha is not None:
        parser.add_argument("-a", "--alpha", type=float, default=default_alpha,
                            help="The width of the model, by default %(default)s.")

    if bw_required is not None:
        parser.add_argument("-bw", "--base_weights", type=str, required=bw_required,
                            help="The base weights to load on model.")


def summary_model(model_path):
    """ CLI entry point to display a model architecture from h5/onnx/fbz file.

    Args:
        model_path (str): Path to the model.
    """
    model = load_model(model_path)
    if isinstance(model, onnx.ModelProto):
        print(onnx.helper.printable_graph(model.graph), file=sys.stdout)
    else:
        model.summary()


def main():
    """ CLI entry point.

    Contains an argument parser with specific arguments depending on the model
    to be created. Complete arguments lists available using the -h or --help
    argument.

    """
    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers(dest="action")
    c_parser = sp.add_parser("create", help="Create an Akida Keras model")
    c_parser.add_argument("-s",
                          "--save_model",
                          type=str,
                          default=None,
                          help="The path/name to use to save the model")
    csp = c_parser.add_subparsers(dest="model",
                                  help="The type of model to be instantiated")
    csp.add_parser("vgg_utk_face", help="A VGG-like UTKFace model")

    csp.add_parser("convtiny_dvs_handy", help="A Convtiny DVS handy model")

    csp.add_parser("convtiny_dvs_gesture", help="A Convtiny DVS gesture model")

    csp.add_parser(
        "ds_cnn_kws",
        help="A Depthwise Separable MobileNet-like model for the Keyword"
        " Spotting example")

    mb_parser = csp.add_parser("mobilenet_imagenet",
                               help="A MobileNet V1 model for Akida")
    add_common_args(mb_parser, default_classes=1000, default_alpha=1.0, default_img_size=224)

    an_parser = csp.add_parser("akidanet_imagenet", help="An AkidaNet model")
    add_common_args(an_parser, default_classes=1000, default_img_size=224, default_alpha=1.0)

    ane_parser = csp.add_parser("akidanet_edge_imagenet",
                                help="An AkidaNet model modified for Akida \
                                edge learning")
    add_common_args(ane_parser, default_classes=1000, bw_required=True)
    ane_parser.add_argument("-bl",
                            "--base_layer",
                            type=str,
                            default="classifier",
                            help="Last layer of the base model.")

    an18_parser = csp.add_parser("akidanet18_imagenet", help="An AkidaNet18 model")
    add_common_args(an18_parser, default_classes=1000, default_img_size=224)

    pnet_parser = csp.add_parser("pointnet_plus_modelnet40", help="A PointNet++ model for Akida")
    pnet_parser.add_argument("-alpha",
                             "--alpha",
                             type=float,
                             default=1.0,
                             help="Network filters multiplier (typically 0.5 , \
                             [1.0]")

    yl_parser = csp.add_parser("yolo_base", help="A YOLOv2 model for detection")
    add_common_args(yl_parser, default_classes=1, default_alpha=0.5, bw_required=False)
    yl_parser.add_argument("-na",
                           "--number_anchors",
                           type=int,
                           default=5,
                           help="The number of anchor boxes")

    csp.add_parser("gxnor_mnist", help="A GXNOR MNIST model for Akida")

    akun_parser = csp.add_parser("akida_unet_portrait128",
                                 help="An Akida U-Net model for Portrait128 segmentation.")
    akun_parser.add_argument("-bw", "--base_weights", type=str, default=None,
                             help="The base AkidaNet weights to use for the encoder.")

    cn_parser = csp.add_parser("centernet", help="A CenterNet model.")
    add_common_args(cn_parser, default_classes=20, bw_required=False)
    cn_parser.add_argument("-i", "--image_size", type=int, default=384,
                           choices=[224, 384],
                           help="The square input image size")

    csp.add_parser("tenn_spatiotemporal_dvs128",
                   help="A TENN spatiotemporal model for DVS128")

    eye_p = csp.add_parser("tenn_spatiotemporal_eye",
                           help="A TENN spatiotemporal model for AIS2024 event-based eyetracking")
    eye_p.add_argument("-reg", "--reg_factor", type=float, default=1e-8,
                       help="The regularization factor, default %(default)s.")

    csp.add_parser("tenn_spatiotemporal_jester",
                   help="A TENN spatiotemporal model for jester video.")

    sparsity_parser = sp.add_parser("sparsity", help="Compute the sparsity of the model")
    sparsity_parser.add_argument("-m", "--model", type=str,
                                 help="Model which sparsity to compute.")
    sparsity_parser.add_argument("-l", "--layer_names", type=str, default=None,
                                 help="Comma-separated list of layers")
    sparsity_parser.add_argument("-ns", "--n_samples", type=int, default=10,
                                 help="The number of the samples used to compute the sparsity")
    sparsity_parser.add_argument("-sa", "--samples", type=str, default=None,
                                 help="The path of the samples file used to compute the sparsity")

    unfuse_parser = sp.add_parser(
        "unfuse", help="Unfuse SeparableConv2D layers of a Keras model")
    unfuse_parser.add_argument("-m", "--model", type=str, required=True, help="Model to unfuse.")

    # Save weights arguments
    w_parser = sp.add_parser(
        "save_weights", help="Store model's weights in an npz.")
    w_parser.add_argument("-m", "--model", type=str, required=True,
                          help="Model to extract weights from.")
    w_parser.add_argument("-w", "--weights_path", type=str,
                          help="Npz file that contains the saved weights.")

    # Load weights arguments
    w_parser = sp.add_parser(
        "load_weights", help="Apply weights to a model from an npz file.")
    w_parser.add_argument("-m", "--model", type=str, required=True,
                          help="Model to apply the weights.")
    w_parser.add_argument("-w", "--weights_path", type=str, required=True,
                          help="Npz file that contains the weights to apply.")
    # summary model
    sum_parser = sp.add_parser(
        "summary",
        help="Display a model architecture from h5/onnx/fbz file.")
    sum_parser.add_argument("-m", "--model", type=str, required=True, help="Model to display.")
    args = parser.parse_args()
    if args.action == "create":
        # Instantiate the wished model
        if args.model == "vgg_utk_face":
            model = vgg_utk_face()
        elif args.model == "convtiny_dvs_handy":
            model = convtiny_dvs(input_shape=(120, 160, 2), classes=9)
        elif args.model == "convtiny_dvs_gesture":
            model = convtiny_dvs(input_shape=(64, 64, 10))
        elif args.model == "ds_cnn_kws":
            model = ds_cnn_kws()
        elif args.model == "pointnet_plus_modelnet40":
            model = pointnet_plus_modelnet40(alpha=args.alpha)
        elif args.model == "mobilenet_imagenet":
            input_shape = (args.image_size, args.image_size, 3)
            model = mobilenet_imagenet(input_shape,
                                       alpha=args.alpha,
                                       classes=args.classes)
        elif args.model == "akidanet_imagenet":
            input_shape = (args.image_size, args.image_size, 3)
            model = akidanet_imagenet(input_shape,
                                      alpha=args.alpha,
                                      classes=args.classes)
        elif args.model == "akidanet_edge_imagenet":
            model = akidanet_edge_imagenet(base_model=args.base_weights,
                                           classes=args.classes,
                                           base_layer=args.base_layer)
        elif args.model == "akidanet18_imagenet":
            input_shape = (args.image_size, args.image_size, 3)
            model = akidanet18_imagenet(input_shape, classes=args.classes)
        elif args.model == "yolo_base":
            model = yolo_base(classes=args.classes,
                              nb_box=args.number_anchors,
                              alpha=args.alpha)
            if args.base_weights is not None:
                model.load_weights(args.base_weights, by_name=True)
        elif args.model == "centernet":
            model = centernet_base(input_shape=(args.image_size, args.image_size, 3),
                                   classes=args.classes)
            if args.base_weights is not None:
                model.load_weights(args.base_weights, by_name=True)
        elif args.model == "gxnor_mnist":
            model = gxnor_mnist()
        elif args.model == "akida_unet_portrait128":
            model = akida_unet_portrait128()
            if args.base_weights is not None:
                model.load_weights(args.base_weights, by_name=True)
        elif args.model == "tenn_spatiotemporal_dvs128":
            model = tenn_spatiotemporal_dvs128()
        elif args.model == "tenn_spatiotemporal_eye":
            model = tenn_spatiotemporal_eye(reg_factor=args.reg_factor)
        elif args.model == "tenn_spatiotemporal_jester":
            model = tenn_spatiotemporal_jester()
        # No need for default behaviour as the command-line parser only accepts
        # valid model types
        model_path = args.save_model
        if model_path is None:
            models_by_name = ("mobilenet_imagenet", "centernet")
            model_path = f"{model.name}.h5" if args.model in models_by_name else f"{args.model}.h5"

        # If needed, add the extension
        if not model_path.endswith(".h5"):
            model_path = f"{model_path}.h5"
        model.save(model_path, include_optimizer=False)
        print(f"Model saved as {model_path}")

    elif args.action == "sparsity":
        if args.layer_names:
            args.layer_names = args.layer_names.split(',')
        model = load_model(args.model, compile_model=False)
        samples = np.load(args.samples)['data'] if args.samples else None
        compute_sparsity(model, args.layer_names, None, samples, args.n_samples, verbose=True)
    elif args.action == "save_weights":
        save_model_weights(
            model_path=args.model,
            weights_path=args.weights_path,
        )
    elif args.action == "load_weights":
        load_model_weights(
            model_path=args.model,
            weights_path=args.weights_path,
        )
    elif args.action == "unfuse":
        model = load_model(args.model)
        unfused_model = unfuse_sepconv2d(model)
        # strip file extension from model path
        model_path = os.path.splitext(args.model)[0]
        # Write new path for unfused model
        model_path += "_unfused.h5"
        # Save unfused model
        unfused_model.save(model_path, include_optimizer=False)
        print(f"{model.name} has been unfused and saved under {model_path}.")
    elif args.action == "summary":
        summary_model(args.model)
