import datetime
import os
import time
from pathlib import Path
import atexit

logs_dir = Path("logs_dir")
logs_dir.mkdir(parents=True, exist_ok=True)
log_file = logs_dir / "log.txt"
__log_handler = log_file.open('a', encoding="utf-8")
atexit.register(__log_handler.close)

def get_mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError as e:
        return -1

def log(msg: str, debug: bool = False):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"

    __log_handler.write(formatted + "\n")
    __log_handler.flush()  # critical for background services

    if debug:
        print(formatted, flush=True)

