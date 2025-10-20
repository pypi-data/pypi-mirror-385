from pathlib import Path
import urllib.request
import zipfile
import io
import shutil

__version__ = "1.1.7"

PACKAGE_DIR = Path(__file__).resolve().parent
RESOURCE_DIR = PACKAGE_DIR / "pymeili_resource"

def ensure_fonts_installed():
    if RESOURCE_DIR.exists():
        print(f"[HINT] Font files found at {RESOURCE_DIR}")
        return

    print(f"[HINT] Font files not found. Downloading from GitHub...")
    url = "https://github.com/VVVICTORZHOU/pymeili3/archive/refs/heads/main.zip"

    try:
        with urllib.request.urlopen(url) as resp:
            with zipfile.ZipFile(io.BytesIO(resp.read())) as z:
                # 找出 repo 根目錄名稱，例如 "pymeili3-main/"
                top_level_dir = z.namelist()[0].split("/")[0] + "/"
                # 解壓整個 zip 到暫存資料夾
                temp_extract_dir = PACKAGE_DIR / "_tmp_fonts"
                z.extractall(temp_extract_dir)

        # 找到解壓出來的 pymeili_resource 目錄
        extracted_resource_dir = temp_extract_dir / top_level_dir / "pymeili_resource"
        if not extracted_resource_dir.exists():
            raise FileNotFoundError(f"No pymeili_resource found in {top_level_dir}")

        # 搬到套件資料夾
        shutil.move(str(extracted_resource_dir), str(RESOURCE_DIR))
        shutil.rmtree(temp_extract_dir)  # 刪除暫存資料夾

        print(f"[OK] Fonts installed at {RESOURCE_DIR}")

    except Exception as e:
        print(f"[FATAL ERROR] Could not download fonts: {e}")
        print(f"[HINT] Please install manually from: {url}")

ensure_fonts_installed()
