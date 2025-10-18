import torch
import torch.nn as nn
import numpy as np
import os

from utils import flatten_sequential, save_binary, save_to_dir


class WDLC():
    def __init__(self, model, input_shape):
        self.model = model
        self.input_shape = input_shape
        self.output_format = "dir"

    def set_output_format(self, format_type):
        """
        Set output format: 'binary' for single file, 'dir' for directory structure.

        """

        if format_type not in ["binary", "dir"]:
            raise ValueError("format_type must be 'binary' or 'dir'")
        self.output_format = format_type


    def compile(self, output_path=None): 
        """
        Extract the graph and weights from a Pytorch model.
        """
        if output_path is None:
            output_path = "model.wdlc" if self.output_format == "binary" else "web_model"
            
        if self.output_format == "dir":
            os.makedirs(output_path, exist_ok=True)

        # Run the model once to extract the computation graph
        dummy_input = torch.randn(1, *self.input_shape)
        scripted = torch.jit.trace(self.model, dummy_input)

        name_to_module = dict(self.model.named_modules())
        layers = []
        weights_dict = {}

        # Walk graph
        for node in scripted.graph.nodes():
            if node.kind() == "prim::CallMethod":
                target = node.inputsAt(0).debugName() # e.g. %fc1

                if target in name_to_module:
                    mod = name_to_module[target]
                    flattened_layers = flatten_sequential(mod, target)
                    
                    
                    for target, mod in flattened_layers:
                        if isinstance(mod, nn.Linear):
                            w_name = f"{target}_weight.npy"
                            b_name = f"{target}_bias.npy"
                            
                            weight_data = mod.weight.detach().cpu().numpy().astype(np.float32)
                            bias_data = mod.bias.detach().cpu().numpy().astype(np.float32)
                            
                            if self.output_format == "dir":
                                np.save(os.path.join(output_path, w_name), weight_data)
                                np.save(os.path.join(output_path, b_name), bias_data)
                            
                            weights_dict[f"{target}_weight"] = weight_data
                            weights_dict[f"{target}_bias"] = bias_data

                            layers.append({
                                "name": target,
                                "type": "linear",
                                "in_features": mod.in_features,
                                "out_features": mod.out_features,
                                "weight": w_name,
                                "bias": b_name
                            })

                        elif isinstance(mod, nn.ReLU):
                            layers.append({
                                "name": target,
                                "type": "relu"
                            })

                        elif isinstance(mod, nn.LeakyReLU):
                            layers.append({
                                "name": target,
                                "type": "leakyReLU",
                                "negative_slope": mod.negative_slope
                            })

                        elif isinstance(mod, nn.Sigmoid):
                            layers.append({
                                "name": target,
                                "type": "sigmoid"
                            })

                        elif isinstance(mod, nn.Tanh):
                            layers.append({
                                "name": target,
                                "type": "tanh"
                            })

                        elif isinstance(mod, nn.SELU):
                            layers.append({
                                "name": target,
                                "type": "selu"
                            })

                        elif isinstance(mod, nn.GELU):
                            layers.append({
                                "name": target,
                                "type": "gelu",
                                "approximate": mod.approximate
                            })

                        elif isinstance(mod, nn.Conv2d):
                            weight_data = mod.weight.detach().cpu().numpy().astype(np.float32)
                            weights_dict[f"{target}_weight"] = weight_data
                            
                            if self.output_format == "dir":
                                np.save(os.path.join(output_path, f"{target}_weight.npy"), weight_data)

                            layer_entry = {
                                "name": target,
                                "type": "conv2d",
                                "in_channels": mod.in_channels,
                                "out_channels": mod.out_channels,
                                "kernel_size": list(mod.kernel_size),
                                "stride": list(mod.stride),
                                "padding": list(mod.padding),
                                "dilation": list(mod.dilation),
                                "groups": mod.groups,
                                "weight": f"{target}_weight.npy"
                            }

                            if mod.bias is not None:
                                bias_data = mod.bias.detach().cpu().numpy().astype(np.float32)
                                weights_dict[f"{target}_bias"] = bias_data
                                layer_entry["bias"] = f"{target}_bias.npy"
                                
                                if self.output_format == "dir":
                                    np.save(os.path.join(output_path, f"{target}_bias.npy"), bias_data)

                            layers.append(layer_entry)

                        elif isinstance(mod, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
                            # added this line to check is gamma & beta is learnable params
                            if not mod.affine:
                                gamma = np.ones(mod.num_features, dtype=np.float32)
                                beta = np.zeros(mod.num_features, dtype=np.float32)
                            else:
                                gamma = mod.weight.detach().cpu().numpy().astype(np.float32)
                                beta  = mod.bias.detach().cpu().numpy().astype(np.float32)

                            running_mean = mod.running_mean.detach().cpu().numpy().astype(np.float32)
                            running_var = mod.running_var.detach().cpu().numpy().astype(np.float32)

                            weights_dict[f"{target}_gamma"] = gamma
                            weights_dict[f"{target}_beta"] = beta
                            weights_dict[f"{target}_running_mean"] = running_mean
                            weights_dict[f"{target}_running_var"] = running_var

                            if self.output_format == "dir":
                                np.save(os.path.join(output_path, f"{target}_gamma.npy"), gamma)
                                np.save(os.path.join(output_path, f"{target}_beta.npy"), beta)
                                np.save(os.path.join(output_path, f"{target}_running_mean.npy"), running_mean)
                                np.save(os.path.join(output_path, f"{target}_running_var.npy"), running_var)

                            layers.append({
                                "name": target,
                                "type": type(mod).__name__.lower(),
                                "num_features": mod.num_features,
                                "eps": mod.eps,
                                "affine": mod.affine,
                                "track_running_stats": mod.track_running_stats,
                                "gamma": f"{target}_gamma.npy",
                                "beta": f"{target}_beta.npy",
                                "running_mean": f"{target}_running_mean.npy",
                                "running_var": f"{target}_running_var.npy"
                            })
                            
                        elif isinstance(mod, nn.LayerNorm):
                            gamma = mod.weight.detach().cpu().numpy().astype(np.float32) if mod.elementwise_affine else None
                            beta = mod.bias.detach().cpu().numpy().astype(np.float32) if mod.elementwise_affine else None

                            weights_dict[f"{target}_gamma"] = gamma
                            weights_dict[f"{target}_beta"] = beta

                            if self.output_format == "dir":
                                if gamma is not None:
                                    np.save(os.path.join(output_path, f"{target}_gamma.npy"), gamma)
                                if beta is not None:
                                    np.save(os.path.join(output_path, f"{target}_beta.npy"), beta)

                            layers.append({
                                "name": target,
                                "type": type(mod).__name__.lower(),
                                "variant": type(mod).__name__,
                                "num_features": mod.normalized_shape,  # LayerNorm uses normalized_shape
                                "eps": mod.eps,
                                "affine": mod.elementwise_affine,
                                "gamma": f"{target}_gamma.npy" if gamma is not None else None,
                                "beta": f"{target}_beta.npy" if beta is not None else None
                            })
                        elif isinstance(mod, (nn.MaxPool1d, nn.MaxPool2d, nn.MaxPool3d)):
                            kernel_size = list(mod.kernel_size) if isinstance(mod.kernel_size, (tuple, list)) else [mod.kernel_size]
                            stride = mod.stride
                            stride_list = (list(stride) if isinstance(stride, (tuple, list)) else ([stride] if stride is not None else None))
                            padding = list(mod.padding) if isinstance(mod.padding, (tuple, list)) else [mod.padding]
                            dilation = list(mod.dilation) if isinstance(mod.dilation, (tuple, list)) else [mod.dilation]

                            dim = 1 if isinstance(mod, nn.MaxPool1d) else 2 if isinstance(mod, nn.MaxPool2d) else 3
                            layers.append({
                                "name": target,
                                "type": f"maxpool{dim}d",
                                "kernel_size": kernel_size,
                                "stride": stride_list,
                                "padding": padding,
                                "dilation": dilation,
                                "ceil_mode": mod.ceil_mode,
                                "return_indices": getattr(mod, "return_indices", False)
                            })

                        elif isinstance(mod, (nn.AvgPool1d, nn.AvgPool2d, nn.AvgPool3d)):
                            kernel_size = list(mod.kernel_size) if isinstance(mod.kernel_size, (tuple, list)) else [mod.kernel_size]
                            stride = mod.stride
                            stride_list = (list(stride) if isinstance(stride, (tuple, list)) else ([stride] if stride is not None else None))
                            padding = list(mod.padding) if isinstance(mod.padding, (tuple, list)) else [mod.padding]

                            dim = 1 if isinstance(mod, nn.AvgPool1d) else 2 if isinstance(mod, nn.AvgPool2d) else 3
                            layers.append({
                                "name": target,
                                "type": f"avgpool{dim}d",
                                "kernel_size": kernel_size,
                                "stride": stride_list,
                                "padding": padding,
                                "ceil_mode": mod.ceil_mode,
                                "count_include_pad": getattr(mod, "count_include_pad", False),
                                "divisor_override": getattr(mod, "divisor_override", None)
                            })

                        elif isinstance(mod, (nn.AdaptiveAvgPool1d, nn.AdaptiveAvgPool2d, nn.AdaptiveAvgPool3d)):
                            out_size = list(mod.output_size) if isinstance(mod.output_size, (tuple, list)) else [mod.output_size]
                            dim = 1 if isinstance(mod, nn.AdaptiveAvgPool1d) else 2 if isinstance(mod, nn.AdaptiveAvgPool2d) else 3
                            layers.append({
                                "name": target,
                                "type": f"adaptiveavgpool{dim}d",
                                "output_size": out_size
                            })

                        elif isinstance(mod, (nn.AdaptiveMaxPool1d, nn.AdaptiveMaxPool2d, nn.AdaptiveMaxPool3d)):
                            out_size = list(mod.output_size) if isinstance(mod.output_size, (tuple, list)) else [mod.output_size]
                            dim = 1 if isinstance(mod, nn.AdaptiveMaxPool1d) else 2 if isinstance(mod, nn.AdaptiveMaxPool2d) else 3
                            layers.append({
                                "name": target,
                                "type": f"adaptivemaxpool{dim}d",
                                "output_size": out_size,
                                "return_indices": getattr(mod, "return_indices", False)
                            })

                        elif isinstance(mod, nn.Unflatten):
                            layers.append({
                                "name": target,
                                "type": "unflatten",
                                "dim": mod.dim,
                                "unflattened_size": list(mod.unflattened_size)
                            })

                        elif isinstance(mod, nn.Flatten):
                            layers.append({
                                "name": target,
                                "type": "flatten",
                                "start_dim": mod.start_dim,
                                "end_dim": mod.end_dim
                            })

        if self.output_format == "binary":
            save_binary(layers, weights_dict, output_path, self.input_shape)
        else:
            save_to_dir(layers, weights_dict, output_path)

        return output_path


        

            
