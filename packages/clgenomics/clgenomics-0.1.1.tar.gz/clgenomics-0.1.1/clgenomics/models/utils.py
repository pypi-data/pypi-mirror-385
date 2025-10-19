import torch
from typing import Tuple


def get_feature_dimension(model: torch.nn.Module, input_length: int) -> int:
    """Utility function to get the output feature dimension of a model given an input length."""
    was_training = model.training
    device = next(model.parameters()).device
    try:
        model.eval()
        with torch.no_grad():
            dummy_input = torch.randn(1, 4, input_length, device=device)
            output = model(dummy_input)
            if isinstance(output, tuple):
                output = output[0]  # If model returns a tuple, take the first element
        return output.shape[1]  # Return the number of channels/features
    finally:
        model.train(mode=was_training)


def split_model(model: torch.nn.Module) -> Tuple[torch.nn.Module, torch.nn.Module]:
    """
    Splits a model into base and head components.
    """
    raise NotImplementedError()

