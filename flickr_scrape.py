#!/usr/bin/env python3
import requests
import string
import os
import util
import tempfile
import shutil
import time

util.mkdirp("data/flickr")

# Flickr image URL template
photo_url = string.Template(
    "https://farm${farmid}.staticflickr.com/${serverid}/${id}_${secret}.jpg"
)

API_KEY = "0b34944b5b61b43ec4fb3dc6389377a6"
TAGS = "yellowstone,landscape"
PER_PAGE = 100
MAX_PAGES = 5   # 🔴 LIMIT pages to avoid infinite scraping

page = 1

while page <= MAX_PAGES:
    print(f"Requesting page {page}...")

    try:
        r = requests.get(
            "https://api.flickr.com/services/rest/",
            params={
                "method": "flickr.photos.search",
                "format": "json",
                "nojsoncallback": 1,
                "api_key": API_KEY,
                "tags": TAGS,
                "tag_mode": "all",
                "page": page,
                "per_page": PER_PAGE,
            },
            timeout=10,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        print("Error contacting Flickr API:", e)
        break

    data = r.json()
    photos = data.get("photos", {}).get("photo", [])

    if not photos:
        print("No more photos found.")
        break

    for photo in photos:
        file_path = os.path.join("data", "flickr", photo["id"] + ".jpg")
        url = photo_url.substitute(
            farmid=photo["farm"],
            serverid=photo["server"],
            id=photo["id"],
            secret=photo["secret"],
        )

        if os.path.isfile(file_path):
            print(file_path, "already exists.")
            continue

        print("Downloading", url)

        try:
            photo_req = requests.get(url, stream=True, timeout=10)
            photo_req.raise_for_status()

            # Atomic write using temp file
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in photo_req.iter_content(1024):
                    if chunk:
                        tmp.write(chunk)

            shutil.move(tmp.name, file_path)

        except requests.RequestException as e:
            print("Failed to download image:", e)
            continue

        # Be polite to Flickr servers
        time.sleep(0.2)

    total_pages = data["photos"]["pages"]
    print(f"Finished page {page} of {total_pages}")

    if page >= total_pages:
        break

    page += 1

print("Flickr image download completed.")

# #!/usr/bin/env python
# import requests
# import string
# import os.path
# import util
# from atomicfile import AtomicFile

# util.mkdirp("data/flickr")

# # URL template for a Flickr image.
# photo_url = string.Template("https://farm${farmid}.staticflickr.com/${serverid}/${id}_${secret}.jpg")
# # Page counter.
# page = 1

# while True:
#     # Search for images with the desired tags.
#     r = requests.get('https://api.flickr.com/services/rest/', params={
#         'method': 'flickr.photos.search',
#         'format': 'json',
#         'nojsoncallback': 1,
#         'api_key': '0b34944b5b61b43ec4fb3dc6389377a6',
#         'tags': 'yellowstone,landscape',
#         'tag_mode': 'all',
#         'page': page,
#     })

#     json = r.json()
#     for photo in json['photos']['photo']:
#         file = "data/flickr/" + photo['id'] + '.jpg'
#         url = photo_url.substitute(farmid=photo['farm'], serverid=photo['server'], id=photo['id'], secret=photo['secret'])

#         # Only try to create the file if it doesn't exist already.
#         if not os.path.isfile(file):
#             print "Downloading " + url + " to " + file + "..."
#             photo_req = requests.get(url)
#             if photo_req.status_code != requests.codes.ok:
#                 print "Error requesting photo."
#                 break

#             # Write the file atomically, so we don't have corrupted images.
#             with AtomicFile(file, 'wb') as fd:
#                 for chunk in photo_req.iter_content(1024):
#                     fd.write(chunk)
#         else:
#             print file + " already exists..."

#     # Continue until we've exhausted all of the pages.
#     if page < json['photos']['pages']:
#         print "Querying page", page, "out of", json['photos']['pages']
#         page += 1
