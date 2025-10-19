### Code here is modified from Jacob's Schreiber's implementation of BPNet, called BPNet-lite:
### https://github.com/jmschrei/bpnet-lite/

import torch


class BPNet(torch.nn.Module):
    """
    Single-class model with base (Sequential) and head (ModuleDict).

    Parameters
    ----------
    n_filters: int, default=512
        Number of convolutional filters.
    n_layers: int, default=8
        Number of residual convolutional layers.
    n_outputs: int, default=2 (positive and negative strand)
        Number of output channels for profile prediction.
    trimming: int, default = (2114 - 1000) // 2 = 557
        Number of positions to trim from each side before deconvolution.
    deconv_kernel_size: int, default=75
        Kernel size for the deconvolution layer.

    forward:
        x: torch.Tensor (N, 4, L)
        returns: tuple of torch.Tensor (N, 2, L) and torch.Tensor (N, 1)
            - y_profile: predicted profiles (logits)
            - y_count: predicted counts (logits)
    """

    def __init__(
        self,
        n_filters: int = 512,
        n_layers: int = 8,
        n_outputs: int = 2,
        trimming: int = (2114 - 1000) // 2,
        deconv_kernel_size: int = 75,
    ):
        super().__init__()

        blocks = [
            torch.nn.Conv1d(4, n_filters, kernel_size=21, padding=10),
            torch.nn.ReLU(),
        ]
        blocks += [
            ResidualConv1d(
                channels=n_filters,
                dilation=2 ** i,
                kernel_size=3
            ) for i in range(1, n_layers + 1)
        ]
        blocks.append(Trim1d(trimming, deconv_kernel_size))
        self.base = torch.nn.Sequential(*blocks)

        self.head = torch.nn.ModuleDict(
            {
                "profile": torch.nn.Conv1d(
                    n_filters, n_outputs, kernel_size=deconv_kernel_size
                ),
                "count": torch.nn.Linear(n_filters, 1),
            }
        )

    def forward(self, x: torch.Tensor):
        embeds = self.base(x)
        y_profile = self.head["profile"](embeds)
        y_count = self.head["count"](embeds.mean(dim=2)).view(embeds.size(0), 1)
        return y_profile, y_count


class BPNetBase(torch.nn.Module):
    def __init__(self, model: 'BPNet' = None, config: dict = None):
        super().__init__()
        if model is not None:
            self.base = model.base
        elif config is not None:
            self.base = BPNet(**config).base
        else:
            raise ValueError("Either model or config must be provided.")

    def forward(self, x):
        return self.base(x)


# ─────────────────────────── helper blocks ────────────────────────────
class ResidualConv1d(torch.nn.Module):
    """1-D convolution with ReLU and skip connection."""

    def __init__(self, channels: int, dilation: int, kernel_size: int = 3):
        super().__init__()
        self.block = torch.nn.Sequential(
            torch.nn.Conv1d(
                channels,
                channels,
                kernel_size=kernel_size,
                padding=dilation,
                dilation=dilation,
            ),
            torch.nn.ReLU(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.block(x)


class Trim1d(torch.nn.Module):
    """
    Slice the length dimension to match the output window
    while keeping enough context for deconvolution.
    """

    def __init__(self, trimming: int, kernel_size: int):
        """
        Parameters
        ----------
        trimming: int
            The number of elements to trim from the input.
        kernel_size: int
            The size of the kernel used in the deconvolution layer.
        """
        super().__init__()
        # self.left = trimming - kernel_size // 2
        # self.right_offset = trimming + kernel_size // 2  # to subtract from end
        self.offset = trimming - kernel_size // 2

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        start = self.offset
        end = x.size(2) - self.offset
        return x[:, :, start:end]
