import torch
import torch.nn.functional as F
from . import register_loss


# Adapted from https://github.com/johahi/training-borzoi
@register_loss('poisson_mn')
def poisson_multinomial_torch(
        y_pred,
        y_true,
        total_weight: float = 0.2,
        epsilon: float = 1e-6,
        rescale: bool = False,
    ):
        """Possion decomposition with multinomial specificity term.

        Args:
          total_weight (float): Weight of the Poisson total term.
          epsilon (float): Added small value to avoid log(0).
        """
        seq_len = y_true.shape[1]

        # add epsilon to protect against tiny values
        y_true += epsilon
        y_pred += epsilon

        # sum across lengths
        s_true = y_true.sum(dim = 1, keepdim=True)
        s_pred = y_pred.sum(dim = 1, keepdim=True)

        # normalize to sum to one
        p_pred = y_pred / s_pred

        # total count poisson loss
        poisson_term = F.poisson_nll_loss(s_pred,s_true, log_input = False, eps = 0,reduction = 'mean')  # B x T
        #print (poisson_term,poisson_term.shape)
        poisson_term /= seq_len
        #print (poisson_term)

        # multinomial loss
        pl_pred = torch.log(p_pred)  # B x L x T
        multinomial_dot = -torch.multiply(y_true, pl_pred)  # B x L x T
        multinomial_term = multinomial_dot.sum(dim = 1)  # B x T
        multinomial_term /= seq_len

        # normalize to scale of 1:1 term ratio
        loss_raw = multinomial_term + total_weight * poisson_term
        if rescale:
            loss_rescale = loss_raw * 2 / (1 + total_weight)
        else:
            loss_rescale = loss_raw

        return loss_rescale.mean()


# Loss used for Enformer - non-log version of PoissonNLLoss
@register_loss('PoissonNLLoss')
def PoissonNLLoss(y_pred,y_true):
    return torch.nn.PoissonNLLLoss(log_input=False)(y_pred,y_true)