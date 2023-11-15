import torch
import torch.nn as nn
import torch.nn.functional as F

class FrameInterpolator(nn.Module):
    """
    A PyTorch neural network module for frame interpolation between two consecutive video frames.
    """
    
    def __init__(self):
        """
        Initialize the FrameInterpolator model with convolutional layers.
        """
        super(FrameInterpolator, self).__init__()

        # Define the convolutional layers
        self.conv1 = nn.Conv2d(in_channels=6, out_channels=16, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=3, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        """
        Define the forward pass of the FrameInterpolator.

        Args:
        - x (Tensor): The input tensor containing stacked frames.

        Returns:
        - Tensor: The output tensor after passing through convolutional layers.
        """
        # Apply ReLU activation function after each convolutional layer except the last one
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        # The final convolutional layer outputs the interpolated frame without an activation function
        x = self.conv3(x)
        return x
