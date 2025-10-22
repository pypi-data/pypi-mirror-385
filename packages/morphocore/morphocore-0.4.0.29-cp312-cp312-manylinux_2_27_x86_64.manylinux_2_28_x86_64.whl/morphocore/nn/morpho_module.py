import torch
import torch.nn as nn
import torch.nn.functional as F


class MorphoModule(nn.Module):
    """
    Common module for Mathematical Morpholocial operations !
    """
    def __init__(self, in_channel: int, out_channel: int, kernel_shape: tuple, channel_merge_mode: str = "sum", dtype: torch.dtype = torch.float32):
        super().__init__()
        self.weight = nn.Parameter(torch.empty((out_channel, in_channel, *kernel_shape), dtype=dtype).uniform_(-0.01, 0.01))
        self.in_channel = in_channel
        self.out_channel = out_channel
        self.channel_merge_mode = channel_merge_mode