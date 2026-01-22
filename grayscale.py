from PIL import Image
import os

src = "data/flickr"
dst = "data/test"

os.makedirs(dst, exist_ok=True)

count = 0
for file in os.listdir(src):
    if file.lower().endswith(".jpg") and count < 5:
        img = Image.open(os.path.join(src, file)).convert("L")
        img.save(os.path.join(dst, "test_" + file))
        count += 1

print("Test images created.")
