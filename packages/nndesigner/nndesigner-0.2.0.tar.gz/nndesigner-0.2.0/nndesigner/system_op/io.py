import torch.nn as nn
import torch
from typing import SupportsInt,Union

class InputLayer(nn.Module):
    def __init__(self, B:Union[int], C:Union[int], H:Union[int], W:Union[int]):
        super(InputLayer, self).__init__()
        self.input_shape = [B, C, H, W]

    def forward(self) -> torch.Tensor:
        x = torch.randn(self.input_shape)
        return x

class OutputLayer(nn.Module):
    def __init__(self):
        super(OutputLayer, self).__init__()

    def forward(self, x:torch.Tensor):
        print("Output:", x.shape)
