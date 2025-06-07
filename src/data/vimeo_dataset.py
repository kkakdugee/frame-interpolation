from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image

class Vimeo90KDataset:
    """
    Dataset loader for Vimeo90K septuplet sequences.

    Directory structure expected:
      <root>/sequences/<first_level>/<second_level>/im1.png
                                               im2.png
                                               im3.png
    """
    def __init__(self, root_dir: str, list_file: str, transform: Optional[callable]=None):
        self.root = Path(root_dir)
        self.transform = transform
        self.sequences = self._load_sequence_paths(list_file)

    def _load_sequence_paths(self, list_file: str) -> List[Tuple[Path, Path, Path]]:
        seqs: List[Tuple[Path, Path, Path]] = []
        with open(list_file, 'r') as f:
            for line in f:
                rel_path = line.strip()  # e.g., "00000/0000"
                if not rel_path:
                    continue
                seq_dir = self.root / 'sequences' / rel_path
                im1 = seq_dir / 'im1.png'
                im2 = seq_dir / 'im2.png'
                im3 = seq_dir / 'im3.png'
                if im1.exists() and im2.exists() and im3.exists():
                    seqs.append((im1, im2, im3))
                else:
                    raise FileNotFoundError(f"Missing frames in {seq_dir}")
        return seqs

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int) -> Tuple[Image.Image, Image.Image, Image.Image]:
        im1_path, im2_path, im3_path = self.sequences[idx]
        im1 = Image.open(im1_path).convert('RGB')
        im2 = Image.open(im2_path).convert('RGB')
        im3 = Image.open(im3_path).convert('RGB')
        if self.transform:
            im1 = self.transform(im1)
            im2 = self.transform(im2)
            im3 = self.transform(im3)
        return im1, im2, im3