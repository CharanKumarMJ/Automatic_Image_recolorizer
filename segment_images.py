#!/usr/bin/env python3
import os
import numpy as np

from skimage.segmentation import slic
from skimage.io import imread
from skimage.util import img_as_float

from constants import *
from atomicfile import AtomicFile
import util


def segment_image(path, n_segments=N_SEGMENTS):
    """
    Segment an image using SLIC superpixels.
    Returns:
        img      : float image
        segments : superpixel labels
    """

    img = img_as_float(imread(path))
    segment_file = f"{path}.{n_segments}.segments.npy"

    # If segmentation already exists, load it
    if os.path.isfile(segment_file):
        return img, np.load(segment_file)

    print("Segmenting", path)

    # If image is grayscale, img.ndim == 2
    if img.ndim == 2:
        segments = slic(
            img,
            n_segments=n_segments,
            compactness=10,
            sigma=1,
            start_label=0,
            channel_axis=None
        )
    else:
        segments = slic(
            img,
            n_segments=n_segments,
            compactness=10,
            sigma=1,
            start_label=0,
            channel_axis=-1
        )

    # segments = slic(
    #     img,
    #     n_segments=n_segments,
    #     compactness=10,
    #     sigma=1,
    #     start_label=0
    # )

    # Ensure parent directory exists
    util.mkdirp(os.path.dirname(segment_file))

    # Atomic save (safe write)
    with AtomicFile(segment_file, "wb") as fd:
        np.save(fd, segments)

    return img, segments


# Optional: segment all images under data/
if __name__ == "__main__":
    for root, _, files in os.walk("data"):
        for file in files:
            if file.lower().endswith(".jpg"):
                segment_image(os.path.join(root, file))


# #!/usr/bin/env python
# import os
# from atomicfile import AtomicFile

# from skimage.segmentation import slic
# from skimage.data import imread
# from skimage.util import img_as_float

# import numpy as np
# from constants import *


# def segment_image(path, n_segments = N_SEGMENTS):
#     img = img_as_float(imread(path))
#     segment_file = path + "." + str(n_segments) + ".segments"
#     if os.path.isfile(segment_file):
#         return img, np.load(segment_file)

#     print "Segmenting ", path
#     segments = slic(img, n_segments=N_SEGMENTS, compactness=10, sigma=1)

#     with AtomicFile(segment_file, 'wb') as fd:
#         np.save(fd, segments)

#     return img, segments

# # When run as a script, segment all of the files in the data directory.
# if __name__ == '__main__':
#     for root, subdirs, files in os.walk('data'):
#         for file in files:
#             path = os.path.join(root, file)
#             if path.endswith(".jpg"):
#                 segment_image(path)
