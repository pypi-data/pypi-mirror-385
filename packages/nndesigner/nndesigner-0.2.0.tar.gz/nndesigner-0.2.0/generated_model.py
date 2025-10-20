import torch
import torch.nn as nn

class GeneratedModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.n1_conv2d_0 = nn.Conv2d(3, 8, kernel_size=3, stride=1, padding=0)

    def forward(self, x):
        # input provided
        x_0 = self.n1_conv2d_0(x)
        return x_0
