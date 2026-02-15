import datetime
import os
import time
from pathlib import Path

logs_dir = Path("logs_dir")
logs_dir.mkdir(parents=True, exist_ok=True)
log_file = logs_dir / "log.txt"

def get_mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError as e:
        return -1

def log(msg, mode:str = "Screen"):
    mode = mode.lower()
    now = datetime.datetime.now().__format__("%I:%M %p")
    if mode in ["screen", "file"]:
        if mode == "screen":
            print(f"[{now}]{msg}", flush=True)
        else:
            with log_file.open("a", encoding="utf-8") as f:
                f.write(f"[{now}]{msg}\n")

