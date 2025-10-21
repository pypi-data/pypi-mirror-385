"""Module wrappers."""

from typing import Any

import torch


class DecoderModuleWrapper(torch.nn.Module):
    """Wrapper for a module that processes features to work in decoder.

    The module should input feature map and produce a new feature map.

    We wrap it to process each feature map in multi-scale features which is what's used
    for most decoders.
    """

    def __init__(
        self,
        module: torch.nn.Module,
    ):
        """Initialize a DecoderModuleWrapper.

        Args:
            module: the module to wrap
        """
        super().__init__()
        self.module = module

    def forward(
        self, features: list[torch.Tensor], inputs: list[torch.Tensor]
    ) -> list[torch.Tensor]:
        """Apply the wrapped module on each feature map.

        Args:
            features: list of feature maps at different resolutions.
            inputs: original inputs (ignored).

        Returns:
            new features
        """
        new_features = []
        for feat_map in features:
            feat_map = self.module(feat_map)
            new_features.append(feat_map)
        return new_features


class EncoderModuleWrapper(torch.nn.Module):
    """Wraps a module that is intended to be used as the decoder to work in encoder.

    The module should input a feature map that corresponds to the original image, i.e.
    the depth of the feature map would be the number of bands in the input image.
    """

    def __init__(
        self,
        module: torch.nn.Module | None = None,
        modules: list[torch.nn.Module] = [],
    ):
        """Initialize an EncoderModuleWrapper.

        Args:
            module: the encoder module to wrap. Exactly one one of module or modules
                must be set.
            modules: list of modules to wrap
        """
        super().__init__()
        if module is not None and len(modules) > 0:
            raise ValueError("only one of module or modules should be set")
        if module is not None:
            self.encoder_modules = torch.nn.ModuleList([module])
        elif len(modules) > 0:
            self.encoder_modules = torch.nn.ModuleList(modules)
        else:
            raise ValueError("one of module or modules must be set")

    def forward(
        self,
        inputs: list[dict[str, Any]],
    ) -> list[torch.Tensor]:
        """Compute outputs from the wrapped module.

        Inputs:
            inputs: input dicts that must include "image" key containing the image to
                process.
        """
        images = torch.stack([inp["image"] for inp in inputs], dim=0)
        cur = [images]
        for m in self.encoder_modules:
            cur = m(cur, inputs)
        return cur
