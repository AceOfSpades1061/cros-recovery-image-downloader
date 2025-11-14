import os
import sys
import time
import requests
from constants import INDEX_URL

def load_index():
    r = requests.get(INDEX_URL)
    r.raise_for_status()
    return r.json()

def find_board_info(index, board, channel="stable", major_version=None):
    board_entry = None
    for key in index.keys():
        if key.lower() == board.lower():
            board_entry = index[key]
            board = key
            break

    if not board_entry:
        raise Exception(f"Could not find board '{board}'")

    images = board_entry.get("images", [])
    if not images:
        raise Exception(f"No images found for board '{board}'!")

    # Filter by channel
    valid_images = [img for img in images if channel.lower() in img.get("channel", "").lower()]
    if not valid_images:
        raise Exception(f"No image found for channel '{channel}'!")

    # Filter by major version
    if major_version is not None:
        filtered = [
            img for img in valid_images
            if img.get("chrome_version", "").startswith(str(major_version) + ".")
        ]
        if not filtered:
            raise Exception(f"No images found with major version {major_version}")
        valid_images = filtered

    latest = max(valid_images, key=lambda img: img.get("last_modified", 0))
    url = latest.get("url")
    if not url:
        raise Exception("No download URL found!")

    return {
        "board": board,
        "version": latest.get("platform_version"),
        "channel": latest.get("channel"),
        "recovery_url": url
    }

def download_image(info, output_dir="recovery_images"):
    os.makedirs(output_dir, exist_ok=True)
    fname = os.path.basename(info["recovery_url"])
    path = os.path.join(output_dir, fname)

    print(f"Downloading {info['recovery_url']} → {path}")

    with requests.get(info["recovery_url"], stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("Content-Length", 0))
        downloaded = 0
        start_time = time.time()

        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)

                if total_size:
                    percent = downloaded / total_size * 100
                    done = int(50 * downloaded / total_size)
                    sys.stdout.write(
                        f"\r[{'#' * done}{'.' * (50 - done)}] {percent:.1f}%"
                    )
                    sys.stdout.flush()

    print("\nDownload complete:", path)
    return path