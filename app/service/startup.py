import os
import re
import requests
from core.config import settings
import pickle
from torchvision import transforms

from data.dataset import ImageWaveformDataset

wavform_dict = None
image_paths = None
test_mega = None
dataset = None
test_indices = None


# -----------------------------
# Load Dataset
# -----------------------------
def load_dataset():
    global waveform_dict
    global image_paths
    global test_mega
    global dataset
    global test_indices

    # -----------------------------
    # Transform
    # -----------------------------
    image_resize_transform = transforms.Compose(
        [
            transforms.Resize(settings.RESIZE_DIM),
        ]
    )

    with open(settings.WAVFORM_DICT_PATH, "rb") as f:
        waveform_dict = pickle.load(f)
    with open(settings.IMAGE_DICT_PATH, "rb") as f:
        image_paths = pickle.load(f)
    with open(settings.TEST_METADATA_PATH, "rb") as f:
        test_meta = pickle.load(f)
    test_indices = test_meta["indices"]
    dataset = ImageWaveformDataset(waveform_dict, image_paths, image_resize_transform)
