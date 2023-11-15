from torch.utils.data import Dataset
import os
import numpy as np
import torch

class FrameInterpolationDataset(Dataset):
    """
    A custom dataset class for frame interpolation, which loads triples of consecutive frames from a directory.
    Each triple consists of two input frames (A and B) and one target frame (C), where frame C is the intermediate
    frame between A and B.
    """
    
    def __init__(self, directory):
        """
        Initialize the dataset with a given directory.

        Args:
        - directory (str): The path to the directory where the frame sequences are stored.
        """
        self.directory = directory
        self.frame_triples = self._create_frame_triples()  # Initialize the list of frame triples

    def _create_frame_triples(self):
        """
        Create a list of tuples representing the frame triples.

        Returns:
        - triples (list): A list of tuples, where each tuple contains paths to frames A, B, and target frame C.
        """
        triples = []
        videos = os.listdir(self.directory)
        for video in videos:
            frames = sorted(os.listdir(os.path.join(self.directory, video)))
            for i in range(len(frames) - 2):
                # Create a tuple of frame A, frame C (target), and frame B
                triples.append((os.path.join(self.directory, video, frames[i]),    # Frame A
                                os.path.join(self.directory, video, frames[i + 2]), # Frame B
                                os.path.join(self.directory, video, frames[i + 1]))) # Frame C (target)
        return triples

    def __len__(self):
        """
        Get the number of frame triples in the dataset.

        Returns:
        - int: The total number of frame triples.
        """
        return len(self.frame_triples)

    def __getitem__(self, idx):
        """
        Retrieve a single item from the dataset at the specified index.

        Args:
        - idx (int): The index of the item.

        Returns:
        - tuple: A tuple containing the concatenated input tensors (frames A and B) and the target tensor (frame C).
        """
        frame_a_path, frame_b_path, frame_c_path = self.frame_triples[idx]
        frame_a = np.load(frame_a_path)
        frame_b = np.load(frame_b_path)
        frame_c = np.load(frame_c_path)
    
        # Convert numpy arrays to PyTorch tensors, ensuring they are float type and channels-first
        frame_a_tensor = torch.from_numpy(frame_a).float().permute(2, 0, 1)
        frame_b_tensor = torch.from_numpy(frame_b).float().permute(2, 0, 1)
        frame_c_tensor = torch.from_numpy(frame_c).float().permute(2, 0, 1)
    
        # Concatenate frames A and B along the channel dimension to form the input tensor
        input_tensor = torch.cat((frame_a_tensor, frame_b_tensor), dim=0)
    
        return input_tensor, frame_c_tensor
