import os
import urllib.request
import zipfile
import shutil
import sys

def install_local_ffmpeg():
    # Detect the venv Scripts folder path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_scripts = os.path.join(base_dir, "venv", "Scripts")
    
    if not os.path.exists(venv_scripts):
        print(f"Error: {venv_scripts} not found. Are you currently in a venv?")
        return
        
    ffmpeg_exe_dest = os.path.join(venv_scripts, "ffmpeg.exe")
    if os.path.exists(ffmpeg_exe_dest):
        print("FFmpeg already exists in venv/Scripts! You are good to go.")
        return

    print("Downloading FFmpeg...")
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = os.path.join(base_dir, "ffmpeg.zip")
    
    urllib.request.urlretrieve(url, zip_path)
    
    print("Extracting FFmpeg...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if member.endswith("ffmpeg.exe"):
                # Extract specifically ffmpeg.exe
                source = zip_ref.open(member)
                with open(ffmpeg_exe_dest, "wb") as target:
                    shutil.copyfileobj(source, target)
                break
                
    # Cleanup
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    print(f"\n✅ SUCCESSFULLY INSTALLED FFMPEG directly into your Virtual Environment!")
    print(f"Path: {ffmpeg_exe_dest}")
    print("\nWhisper will now work immediately without any PATH issues. Run `uvicorn app.main:app --reload` securely.")

if __name__ == "__main__":
    install_local_ffmpeg()
