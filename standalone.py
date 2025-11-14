# made with lazyvim and ChromeOS text app
import requests
import os
import sys
import time

INDEX_URL = "https://cdn.jsdelivr.net/gh/MercuryWorkshop/chromeos-releases-data/data.json" # thank you mercury workshop :DD
CROSBREAKER = "Join the crosbreaker discord!"
CREDITS = "Made by AceOfSpades1061, Database by Mercury Workshop"

print(" ▄████▄        ██▀███        ██▓     ▓█████▄     ") # cool ascii art
print("▒██▀ ▀█       ▓██ ▒ ██▒     ▓██▒     ▒██▀ ██▌    ")
print("▒▓█    ▄      ▓██ ░▄█ ▒     ▒██▒     ░██   █▌    ")
print("▒▓▓▄ ▄██▒     ▒██▀▀█▄       ░██░     ░▓█▄   ▌    ")
print("▒ ▓███▀ ░ ██▓ ░██▓ ▒██▒ ██▓ ░██░ ██▓ ░▒████▓  ██▓")
print("░ ░▒ ▒  ░ ▒▓▒ ░ ▒▓ ░▒▓░ ▒▓▒ ░▓   ▒▓▒  ▒▒▓  ▒  ▒▓▒")
print("  ░  ▒    ░▒    ░▒ ░ ▒░ ░▒   ▒ ░ ░▒   ░ ▒  ▒  ░▒ ")
print("░         ░     ░░   ░  ░    ▒ ░ ░    ░ ░  ░  ░  ")
print("░ ░        ░     ░       ░   ░    ░     ░      ░ ")
print("░          ░             ░        ░   ░        ░ ")
time.sleep(1)
print(CREDITS)
time.sleep(1)
print(CROSBREAKER) # do join it
time.sleep(1)
print("feel free to modify this in anyway, just keep my username and i'm fine with it! :D")
print("or else.")
time.sleep(1) # it is time to sleep for 1

def load_index():
    r = requests.get(INDEX_URL)
    r.raise_for_status()
    return r.json()

def find_board_info(index, board, channel="stable", major_version=None):
    # tries to find the board in a case-insensitive way
    board_entry = None
    for key in index.keys():
        if key.lower() == board.lower():
            board_entry = index[key]
            board = key  # exact casing from JSON
            break
    if not board_entry:
        raise Exception(f"Could not find board '{board}' in the index!")
    
    images = board_entry.get("images", [])
    if not images:
        raise Exception(f"No images found for board '{board}'!")

    # Filter by channel (stable, dev, beta)
    valid_images = [img for img in images if channel.lower() in img.get("channel", "").lower()]
    if not valid_images:
        raise Exception(f"No image found for board '{board}' on channel '{channel}'!")

    if major_version:
        filtered = []
    for img in valid_images:
        chrome_ver = img.get("chrome_version", "")
        if chrome_ver.startswith(str(major_version) + "."):
            filtered.append(img)
    if not filtered:
        raise Exception(f"No image found for board '{board}' with major Chrome version '{major_version}'!")
    valid_images = filtered


    # OMG IT'S THE LAMBDA HALF-LIFE REFERENCE NO WAY :ooo
    latest = max(valid_images, key=lambda img: img.get("last_modified", 0))
    url = latest.get("url")
    if not url:
        raise Exception(f"No data found for the latest image of board '{board}'!")

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
        chunk_size = 8192
        start_time = time.time()
        last_update = 0
        update_interval = 0.3

        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                downloaded += len(chunk)

                if total_size:
                    now = time.time()
                    if now - last_update >= update_interval:
                        done = int(50 * downloaded / total_size)
                        percent = downloaded / total_size * 100
                        elapsed = now - start_time
                        speed = downloaded / elapsed  # bytes per second
                        remaining_time = (total_size - downloaded) / speed
                        mins, secs = divmod(int(remaining_time), 60)

                        sys.stdout.write(
                            f"\r[{'#' * done}{'.' * (50 - done)}] "
                            f"{percent:.1f}% - ETA {mins}m {secs}s"
                        )
                        sys.stdout.flush()
                        last_update = now

    print("\nDownload complete:", path)
    return path

if __name__ == "__main__":
    board = input("Enter board name: ").strip()
    channel = input("Enter channel (stable if empty): ").strip() or "stable"
    major_version = input("Enter major version (leave empty for latest): ").strip() or None

    idx = load_index()
    info = find_board_info(idx, board, channel, major_version)
    print(f"Found {board} {channel} version {info['version']}")
    download_image(info)
