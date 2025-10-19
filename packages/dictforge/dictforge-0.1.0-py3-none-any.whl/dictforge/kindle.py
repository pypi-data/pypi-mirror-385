import os
import platform
from pathlib import Path


def guess_kindlegen_path() -> str:
    # Kindle Previewer 3 bundles kindlegen internally
    system = platform.system()
    candidates = []
    if system == "Darwin":
        candidates.append(
            "/Applications/Kindle Previewer 3.app/Contents/MacOS/lib/fc/bin/kindlegen",
        )
    elif system == "Windows":
        home = os.environ.get("USERPROFILE") or os.environ.get("HOMEPATH") or "C:\\Users\\Public"
        candidates.append(
            str(Path(home) / "AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe"),
        )
    else:
        # On Linux, user typically passes path manually or uses Wine
        pass

    for c in candidates:
        if Path(c).exists():
            return c
    return ""
