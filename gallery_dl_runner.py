"""
gallery_dl_runner.py
Thin subprocess entry point for gallery_dl.
Called by the frozen GalleryDL-GUI.exe as a worker process:
  GalleryDL-GUI.exe --run-gallery-dl <args...>
"""
import sys
from gallery_dl import main as gallery_dl_main

if __name__ == "__main__":
    sys.exit(gallery_dl_main())
