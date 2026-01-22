#!/usr/bin/env python3
import os
from atomicfile import AtomicFile
from PIL import Image

# Desired normalized image size
DESIRED_SIZE = (500, 500)

for root, _, files in os.walk("data"):
    for file in files:
        if not file.lower().endswith(".jpg"):
            continue

        path = os.path.join(root, file)
        print("Opening", path)

        try:
            with Image.open(path) as im:
                im = im.convert("RGB")

                if im.size != DESIRED_SIZE:
                    print("Resizing", path, "to", DESIRED_SIZE)

                    # Resize with high-quality filter
                    im = im.resize(DESIRED_SIZE, Image.LANCZOS)

                    # Atomic write to avoid corruption
                    with AtomicFile(path, "wb") as fd:
                        im.save(fd, format="JPEG", quality=95)

        except Exception as e:
            print("Error processing", path, ":", e)

# #!/usr/bin/env python
# import os
# from atomicfile import AtomicFile
# from PIL import Image

# # The desired size that all images in the data directory should
# # be normalized to.
# DESIRED_SIZE = (500, 500)

# for root, subdirs, files in os.walk('data'):
#     for file in files:
#         path = os.path.join(root, file)
#         print "Opening " + path
#         im = Image.open(path)
#         if im.size != DESIRED_SIZE:
#             print "Cropping / resizing", path, " to ", DESIRED_SIZE
