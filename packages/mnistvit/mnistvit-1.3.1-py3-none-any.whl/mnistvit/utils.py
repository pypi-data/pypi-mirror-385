import json
import os
from pathlib import Path
from typing import Any

import torch

from .model import VisionTransformer


def save_model(
    config: dict[str, str | int | float],
    state_dict: dict[str, Any],
    model_dir: str | os.PathLike,
) -> None:
    """Saves the vision transformer configuration and model state to a directory.

    Args:
        config (dict): Model configuration with all keyword arguments to initialize the
            model.
        state_dict (dict): The state of the model.
        model_dir (str or os.PathLike): Directory to save the model to.
    """
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(model_dir, "config.json"), "w") as config_file:
        json.dump(config, config_file, indent=4)
    torch.save(state_dict, os.path.join(model_dir, "model.pt"))


def load_model(
    model_dir: str | os.PathLike, device: torch.device = "cpu"
) -> VisionTransformer:
    """Loads the model from a directory.

    Args:
        model_dir (str or os.PathLike): Directory to load the model from.
        device (torch.device, optional): Device to load the model onto.
            Default: `'cpu'`.

    Returns:
        mnistvit.model.VisionTransformer: The loaded model.
    """
    with open(os.path.join(model_dir, "config.json"), "r") as config_file:
        config = json.load(config_file)
    model = VisionTransformer(**config)
    state_dict = torch.load(
        os.path.join(model_dir, "model.pt"), map_location=torch.device("cpu")
    )
    model.load_state_dict(state_dict)
    model = model.to(device)
    return model
