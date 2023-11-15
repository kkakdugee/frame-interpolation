# Frame Interpolation

## Description
The Frame Interpolation project introduces an approach to enhance video playback smoothness by intelligently increasing the frame rate. Utilizing a convolutional neural network techniques built with PyTorch, this tool interpolates and inserts new frames between existing ones, effectively transforming choppy videos into fluid motion sequences.

## Installation
Make sure to have [Python](https://www.python.org/downloads/) (version 3.6 or higher) and [PyTorch](https://pytorch.org/get-started/locally/) installed. Then, run the following command to install the required dependencies:

```
pip install -r requirements.txt
```

## Preview
<table>
  <tr>
    <td>Original Video (24 fps)</td>
    <td>1st Passthrough (48 fps)</td>
    <td>2nd Passthrough (96 fps)</td>
  </tr>
  <tr>
    <td><a href="https://github-production-user-asset-6210df.s3.amazonaws.com/75061722/283003319-21959c55-6a8a-4950-af87-57f0bdaf8b7d.mp4">
    </a></td>
    <td><a href="https://github-production-user-asset-6210df.s3.amazonaws.com/75061722/283004949-bcbe6477-911f-41ac-9c9e-72d92589e40e.mp4">
    </a></td>
    <td><a href="https://github-production-user-asset-6210df.s3.amazonaws.com/75061722/283005177-ce09450b-8a0f-4d44-951e-5179d16e8549.mp4">
    </a></td>
  </tr>
</table>

## Usage
Execute `runner.py` to begin. Select between preprocessing data or generating an interpolated video. To train the model, preprocess your data first, followed by running `model_training.py`.