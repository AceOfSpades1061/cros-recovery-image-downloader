from banners import show_banner
from recovery import load_index, find_board_info, download_image

if __name__ == "__main__":
    show_banner()

    board = input("Enter board name: ").strip()
    channel = input("Enter channel (stable if empty): ").strip() or "stable"
    major_version = input("Enter major version (leave empty for latest): ").strip()
    major_version = major_version if major_version else None

    idx = load_index()
    info = find_board_info(idx, board, channel, major_version)

    print(f"Found {info['board']} {info['channel']} version {info['version']}")
    download_image(info)