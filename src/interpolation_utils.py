import os
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
from model import UNet

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = UNet().to(device)
checkpoint_path = './unet_trained.pth'
if (os.path.exists(checkpoint_path)):
    checkpoint = torch.load('./unet_trained.pth', map_location=device)
    model.load_state_dict(checkpoint)
    model.eval()

_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])

def naive_interpolate(frame_a: Image.Image, frame_b: Image.Image) -> Image.Image:
    """
    Simple midpoint interpolation: average each pixel.
    """
    a = np.array(frame_a).astype(np.float32)
    b = np.array(frame_b).astype(np.float32)
    mid = ((a + b) / 2).astype(np.uint8)
    return Image.fromarray(mid)

def deep_interpolate(frame_a: Image.Image, frame_b: Image.Image) -> Image.Image:
    """
    Use the pretrained InterpNet to predict the in-between frame.
    """
    # Preprocess input frames
    a = _transform(frame_a).unsqueeze(0).to(device)  # [1,3,H,W]
    b = _transform(frame_b).unsqueeze(0).to(device)
    # Concatenate along channel dim: [1,6,H,W]
    inp = torch.cat([a, b], dim=1)

    # Inference
    with torch.no_grad():
        pred = model(inp)            # shape [1,3,H,W]
        pred = pred.squeeze(0)       # [3,H,W]

    # Convert tensor to PIL Image
    pred = pred.cpu().clamp(0, 1)
    arr = (pred.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    return Image.fromarray(arr)
