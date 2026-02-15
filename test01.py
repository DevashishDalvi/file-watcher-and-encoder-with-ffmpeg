import datetime
import os
import time
from pathlib import Path

def get_mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError as e:
        return -1

def log(msg, mode:str = "Screen"):
    mode = mode.lower()
    now = datetime.datetime.now()
    if mode in ["screen", "file"]:
        if mode == "screen":
            print(f"[{now: %I:%M %p}]{msg}", flush=True)
        else:
            pass

