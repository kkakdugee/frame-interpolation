# Frame Interpolation

## Description
The Frame Interpolation project introduces an approach to enhance video playback smoothness by intelligently increasing the frame rate. Utilizing a convolutional neural network techniques built with PyTorch, this tool interpolates and inserts new frames between existing ones, effectively transforming choppy videos into fluid motion sequences.

## Installation
Make sure to have [Python](https://www.python.org/downloads/) (version 3.6 or higher) and [PyTorch](https://pytorch.org/get-started/locally/) installed. Then, run the following command to install the required dependencies:

```
pip install -r requirements.txt
```

## Preview
### Original Video (24 FPS)
https://github.com/kkakdugee/frame-interpolation/assets/75061722/62c335b8-faa7-4885-99cd-2c3a69d2e8e3

### 1st Passthrough (48 FPS)
https://github.com/kkakdugee/frame-interpolation/assets/75061722/25e554ca-556e-413b-bc93-21385eb26dd0





## Usage
Execute `runner.py` to begin. Select between preprocessing data or generating an interpolated video. To train the model, preprocess your data first, followed by running `model_training.py`.
