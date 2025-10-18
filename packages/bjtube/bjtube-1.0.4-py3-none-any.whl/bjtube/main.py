import os
import sys
import subprocess
from colorama import Fore, Style, init
from tqdm import tqdm
import yt_dlp

init(autoreset=True)

def check_and_install(package):
    try:
        __import__(package)
        print(f"{Fore.GREEN}✅ {package} is already installed.")
    except ImportError:
        choice = input(f"{Fore.YELLOW}⚠️  {package} not found. Install it now? (y/n): ").strip().lower()
        if choice == 'y':
            print(f"{Fore.CYAN}📦 Installing {package} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        else:
            print(f"{Fore.RED}❌ Cannot continue without {package}. Exiting.")
            sys.exit(1)

def show_resolutions(info):
    print(f"\n🎬 {Fore.CYAN}Available Resolutions:\n" + "-" * 60)
    for f in info['formats']:
        fmt_id = f.get("format_id", "N/A")
        ext = f.get("ext", "N/A")
        resolution = f.get("resolution") or f"{f.get('width', 'N/A')}x{f.get('height', 'N/A')}"
        acodec = f.get("acodec", "none")
        vcodec = f.get("vcodec", "none")

        if vcodec != "none" and acodec != "none":
            media_type = f"{Fore.YELLOW}Video+Audio"
        elif vcodec != "none":
            media_type = f"{Fore.BLUE}Video Only"
        elif acodec != "none":
            media_type = f"{Fore.GREEN}Audio Only"
        else:
            media_type = f"{Fore.RED}Unknown"

        print(f"{Fore.WHITE}ID: {fmt_id:<8} | Ext: {ext:<4} | Res: {resolution:<9} | {media_type}")
    print("-" * 60)

def main():
    print(f"{Fore.CYAN}🎬 bjtube - YouTube Downloader by Babar Ali Jamali")
    print(f"{Fore.CYAN}" + "-" * 50)

    # Check and install dependencies
    print(f"{Fore.YELLOW}📦 Checking and installing dependencies...")
    for pkg in ["yt_dlp", "tqdm", "colorama"]:
        check_and_install(pkg)

    # Ask user for YouTube URL
    url = input(f"\n{Fore.CYAN}📺 Enter YouTube video URL: ").strip()
    if not url:
        print(f"{Fore.RED}❌ No URL entered. Exiting.")
        sys.exit(1)

    ydl_opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    # Show available formats
    show_resolutions(info)

    # Ask user for format ID
    fmt_id = input(f"\n{Fore.CYAN}🔢 Enter format ID to download (e.g., 22): ").strip()
    if not fmt_id:
        print(f"{Fore.RED}❌ No format selected. Exiting.")
        sys.exit(1)

    # Confirm download path
    output_template = "%(title)s.%(ext)s"
    ydl_opts = {
        "format": fmt_id,
        "outtmpl": output_template,
        "progress_hooks": [lambda d: tqdm(total=100, desc="Downloading", unit="%", position=0).update(d.get('downloaded_bytes', 0))]
    }

    print(f"\n{Fore.CYAN}📥 Starting download...\n")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print(f"\n{Fore.GREEN}✅ Download complete!")

if __name__ == "__main__":
    main()
