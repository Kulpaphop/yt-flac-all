import os
import re
from yt_dlp import YoutubeDL
from PIL import Image
import requests
import subprocess
import sys
import zipfile
import io
import ctypes

# pip install requests Pillow yt_dlp
# winget install Python.Python.3.14

if not os.path.exists(".//Output"):
    os.makedirs(".//Output")
if not os.path.exists(".//thumb-add"):
    os.makedirs(".//thumb-add")

metadata = {}
target_url = {}
music_folder = ".//Output//"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def check_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg not found.")
        return False

def install_ffmpeg():
    print("Downloading FFmpeg build for Windows...")
    url = "https://github.com/GyanD/codexffmpeg/releases/download/8.0.1/ffmpeg-8.0.1-full_build.zip"
    response = requests.get(url)
    response.raise_for_status()
    print("Extracting FFmpeg...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall("ffmpeg-temp")
    extracted_dir = [d for d in os.listdir("ffmpeg-temp") if d.startswith("ffmpeg")][0]
    bin_path = os.path.join("ffmpeg-temp", extracted_dir, "bin")
    target_dir = "C:\\ffmpeg"
    os.makedirs(target_dir, exist_ok=True)
    for file in os.listdir(bin_path):
        src = os.path.join(bin_path, file)
        dst = os.path.join(target_dir, file)
        if os.path.exists(dst):
            os.remove(dst)
        os.rename(src, dst)
    print(f"FFmpeg installed to {target_dir}")
    ffmpeg_dir = r"C:\ffmpeg"
    cmd = f'[Environment]::SetEnvironmentVariable("Path", $env:Path + ";{ffmpeg_dir}", "Machine")'
    subprocess.run(["powershell", "-Command", cmd], check=True)
    print("FFmpeg installation completed. Restart the application to use FFmpeg.")
    os.system("pause" if os.name == "nt" else "")
    os._exit(0)

def add_flac_cover(flac_path: str, cover_path: str):
    cmd = [
        "ffmpeg",
        "-i", flac_path,
        "-i", cover_path,
        "-map", "0:a",
        "-map", "1:v",
        "-c", "copy",
        "-disposition:v", "attached_pic",
        "-metadata:s:v", "title=Album cover",
        "-metadata:s:v", "comment=Cover (front)",
        "-y",
        music_folder + flac_path
    ]
    subprocess.run(cmd, check=True)
    os.remove(flac_path)
    return

def crop_to_square(image_path, output_path):
    img = Image.open(image_path)
    width, height = img.size
    target_size = height
    left = (width - target_size) // 2
    top = 0
    right = left + target_size
    bottom = height
    img_cropped = img.crop((left, top, right, bottom))
    img_cropped.save(output_path, "JPEG")
    return

def add_thumb(img_url, flac_path):
    if sel == "5":
        print("Using user provided thumbnail from thumb-add folder.")
        add_flac_cover(flac_path, ".//thumb-add//thumb.png")
        return
    response = requests.get(img_url)
    if not(response.status_code == 200):
        print("Failed to download image.")
        os._exit(1)
    open(".//maxres.webp", "wb").write(response.content)
    crop_to_square(".//maxres.webp", ".//thumb.jpg")
    add_flac_cover(flac_path, ".//thumb.jpg")
    return


def url_info(url):
    global metadata
    with YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
    metadata = {"title": info["title"], "thumbnail": info["thumbnail"]}
    return

def sel1(youtube_url):
    url_info(youtube_url)
    def _safe_filename(s): return re.sub(r'[<>:\\"/\\|?*]', '_', s)
    safe_title = _safe_filename(metadata['title'])
    out_template = f"{safe_title}.%(ext)s"
    ydl_opts = {
        'extractaudio': True,
        'format': 'bestaudio',
        'audioformat': "flac",
        'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
                'preferredquality': '0',
            }, {
                'key': 'FFmpegMetadata',
            }
        ],
        'add_metadata': True,
        'outtmpl': out_template,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    add_thumb(metadata["thumbnail"], f"{safe_title}.flac")
    print(f"Download completed. file saved as: {safe_title}.flac")
    return

def sel2(youtube_url):
    url_info(youtube_url)
    def _safe_filename(s): return re.sub(r'[<>:\\"/\\|?*]', '_', s)
    safe_title = _safe_filename(metadata['title'])
    out_template = f"{safe_title}.%(ext)s"
    ydl_opts = {
        'extractaudio': True,
        'format': 'bestaudio',
        'audioformat': "flac",
        'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
                'preferredquality': '0',
            }, {
                'key': 'FFmpegMetadata',
            }
        ],
        'add_metadata': True,
        'outtmpl': out_template,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    print(f"Download completed. file saved as: {safe_title}.flac")
    return

def sel3(youtube_url):
    url_info(youtube_url)
    response = requests.get(metadata["thumbnail"])
    if not(response.status_code == 200):
        print("Failed to download image.")
        os._exit(1)
    open(".//thumbnail.webp", "wb").write(response.content)
    print(f"Download completed. file saved as: thumbnail.webp")
    return

def sel4(youtube_audio_url, youtube_thumb_url):
    url_info(youtube_audio_url)
    def _safe_filename(s): return re.sub(r'[<>:\\"/\\|?*]', '_', s)
    safe_title = _safe_filename(metadata['title'])
    out_template = f"{safe_title}.%(ext)s"
    ydl_opts = {
        'extractaudio': True,
        'format': 'bestaudio',
        'audioformat': "flac",
        'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
                'preferredquality': '0',
            }, {
                'key': 'FFmpegMetadata',
            }
        ],
        'add_metadata': True,
        'outtmpl': out_template,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_audio_url])
    
    url_info(youtube_thumb_url)
    add_thumb(metadata["thumbnail"], f"{safe_title}.flac")
    print(f"Download completed. file saved as: {safe_title}.flac")
    return

def clear_temp_files():
    temp_files = [".//maxres.webp", ".//thumb.jpg"]
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
    return

def main():
    while True:
        os.system("cls" if os.name == "nt" else "")
        global target_url
        print(\
            "=====================================================\n"\
            "        YouTube .Flac Audio Downloader (All)\n"\
            "=====================================================\n"\
            "[1] Download as FLAC with thumbnail (i.ytimg.com)\n"\
            "[2] Download as FLAC without thumbnail\n"\
            "[3] Download only thumbnail (i.ytimg.com)\n"\
            "[4] Download as FLAC with thumbnail (Link + Audio)\n"\
            "[5] Download as FLAC with local 'thumb-add' png image\n"\
            "[6] Quit\n"\
            "=====================================================\n"\
        )
        global sel
        sel = input("Select an option [1-6]: ")
        match sel:
            case "1":
                target_url = input("Enter YouTube URL: ")
                sel1(target_url)
            case "2":
                target_url = input("Enter YouTube URL: ")
                sel2(target_url)
            case "3":
                target_url = input("Enter YouTube URL: ")
                sel3(target_url)
            case "4":
                target_audio_url = input("Enter YouTube Audio URL: ")
                target_thumb_url = input("Enter YouTube Thumb URL: ")
                sel4(target_audio_url, target_thumb_url)
            case "5":
                target_url = input("Enter YouTube URL: ")
                print("Waiting for user add thumb.png image to thumb_add folder...\npress Enter to continue")
                os.system("pause > nul" if os.name == "nt" else "")
                if not os.path.exists(".//thumb-add//thumb.png"):
                    print("No thumbnail image found in thumb-add folder. Exiting.")
                    os.system("pause" if os.name == "nt" else "")
                    continue
                sel1(target_url)
            case "6":
                print("Exiting...")
                break
            case _:
                continue
        clear_temp_files()
        break
    return


if __name__ == "__main__":
    # INIT
    os.system("title YouTube Audio Downloader Devlopment" if os.name == "nt" else "")
    
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    if not check_ffmpeg_installed():
        install_ffmpeg()
        os._exit(0)

    main()

    # Before exit
    os.system("echo Press any key to exit... && pause > nul" if os.name == "nt" else "")
