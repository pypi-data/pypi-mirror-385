import torch
import torch.nn as nn
from . import register_loss

## Implementation of label aware MSE loss for contrastive learning
# Dual MSE part adapted from: https://github.com/shirondru/enformer_fine_tuning


def masked_mse(y_hat, y, sample_weights=None):
    """
    removes NaNs from y (for example, when someone is missing data from a particular tissue)
    """
    mask = torch.isnan(y)
    if sample_weights is None:
        mse = torch.mean((y[~mask] - y_hat[~mask]) ** 2)
    else:
        # Apply sample weights to the squared errors
        squared_errors = (y[~mask] - y_hat[~mask]) ** 2
        weights = sample_weights[~mask] if sample_weights.shape[0] == y.shape[0] else sample_weights
        mse = torch.sum(squared_errors * weights) / torch.sum(weights)
    return mse


def get_diff_one_gene(y, y_hat):
    """
    Calculates pairwise differences between observed expression values among different people,
    as well as pairwise differences between predicted expression values among different people.
    Returns the difference between these matrices

    Pairwise difference between each unique pair of observed expression values within the batch,
    and performed the same operation for predicted expression values.
    Then took the mean squared difference between these two pairwise difference vectors.
    """
    true_differences = y.unsqueeze(1) - y
    predicted_differences = y_hat.unsqueeze(1) - y_hat
    diff = predicted_differences - true_differences
    return diff


def remove_l_tri_flatten_3d(diff, sample_weights=None):
    """
    Removes the lower triangle of `diff`, the difference between pairwise observed differences
    and pairwise predicted differences. Thus, it keeps only pairwise comparisons between different,
    unique pairs of people.
    This handles the case when training on multiple tissues at the same time and the matrix is 3D.
    Returns a flattened array.
    """
    # Create a mask for the upper triangle
    mask_2d = torch.triu(
        torch.ones(diff.shape[0:2], dtype=torch.bool), diagonal=1
    )  # everything above diagonal is True, everything else is False.
       # So things are True when it is the paired differences between a person and someone else

    mask_3d = mask_2d.unsqueeze(
        -1
    ).repeat(
        1, 1, diff.shape[-1]
    )  # Make this mask 3D. So the same 2D matrix is repeated along the third dimension,
       # so the same mask is applied to each tissue in the tissue dimension
    upper_tri_3d = torch.where(
        mask_3d.to(diff.device), diff, torch.tensor(float("nan")).to(diff.device)
    )  # convert False values to NaN and returns the diff values where True.
       # Uses the 3d mask as the condition

    # Flatten and remove NaN values
    flat = upper_tri_3d.flatten()
    flat_valid = flat[~torch.isnan(flat)]

    if sample_weights is None:
        return flat_valid
    else:
        # Create pairwise weights and apply the same masking
        batch_size = diff.shape[0]
        pair_weights = torch.zeros((batch_size, batch_size), device=diff.device)
        for i in range(batch_size):
            for j in range(batch_size):
                pair_weights[i, j] = (sample_weights[i] + sample_weights[j]) / 2

        pair_weights_3d = pair_weights.unsqueeze(-1).repeat(1, 1, diff.shape[-1])
        weights_upper_tri = torch.where(
            mask_3d.to(diff.device), pair_weights_3d, torch.tensor(float("nan")).to(diff.device)
        )
        weights_flat = weights_upper_tri.flatten()
        weights_valid = weights_flat[~torch.isnan(weights_flat)]

        return flat_valid, weights_valid


def compute_contrastive_loss(target, input, sample_weights=None):
    """
    Helper function to compute contrastive loss with optional sample weighting
    """
    diff = get_diff_one_gene(target, input)

    if sample_weights is None:
        flat = remove_l_tri_flatten_3d(diff)
        return torch.mean(flat**2)
    else:
        flat, weights = remove_l_tri_flatten_3d(diff, sample_weights)
        return torch.sum((flat**2) * weights) / torch.sum(weights)


@register_loss()
class label_aware_dual_MSEloss(nn.Module):
    """
    Label aware dual MSE loss function

    This loss function is a combination of two terms: the mean squared error (MSE) between the
    predicted and observed expression values, and the mean squared difference between the pairwise
    differences of the predicted and observed expression values. The latter term is used to ensure
    that the model captures the relationships between different people in the dataset.

    Reference: https://github.com/shirondru/enformer_fine_tuning
    """
    def __init__(
        self,
        ref_y,
        alpha=0.5,
        rescale=True,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    ) -> None:
        super(label_aware_dual_MSEloss, self).__init__()
        if ref_y is None:
            raise ValueError(
                "ref_y cannot be None for label_aware_dual_MSEloss. "
                "This usually happens when loading a model from checkpoint. "
                "Please provide a valid ref_y value when creating the loss function."
            )
        self.ref_y = torch.tensor(ref_y).to(device)
        self.alpha = alpha
        self.rescale = rescale

    def forward(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        # Calculate sample weights based on distance from reference
        # ref_y is always a single value, so calculate per-sample weights
        per_sample_diff = torch.abs(self.ref_y - target) / (
            torch.abs(self.ref_y) + torch.abs(target) + 1e-8
        )
        sample_weights = torch.clamp(per_sample_diff, min=0.1, max=2.0)

        # Apply weighted loss components using modified functions
        mse = masked_mse(input, target, sample_weights)
        contrastive_term = compute_contrastive_loss(target, input, sample_weights)

        if self.rescale:
            if isinstance(self.rescale, bool):
                # Dynamic rescaling - rescale terms to have similar magnitudes
                mse_detached = mse.detach()
                contrastive_detached = contrastive_term.detach()

                # Avoid division by zero
                if (
                    contrastive_detached > 1e-8
                    and mse_detached > 1e-8
                    and contrastive_detached < mse_detached
                ):
                    scale_factor = mse_detached / contrastive_detached
                    contrastive_term = contrastive_term * scale_factor
            else:
                # Fixed rescaling - use provided scale factor
                contrastive_term = contrastive_term * self.rescale

            loss = (self.alpha * mse) + ((1 - self.alpha) * contrastive_term)
        else:
            # weight contrastive term and mse term by alpha
            loss = (self.alpha * mse) + ((1 - self.alpha) * contrastive_term)

        return loss
