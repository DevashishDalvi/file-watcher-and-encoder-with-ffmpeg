import time
from datetime import datetime as dt
# from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver as Observer

class WatcherHandler(FileSystemEventHandler):
    # Triggered when a file or directory is modified
    def on_modified(self, event):
        print(f"[{dt.now()}] Modified: {event.src_path}")

    # Triggered when a new file or directory is created
    def on_created(self, event):
        print(f"[{dt.now()}]Created: {event.src_path}")

    # Triggered when a file or directory is deleted
    def on_deleted(self, event):
        print(f"[{dt.now()}]Deleted: {event.src_path}")

    # Triggered when a file or directory is moved/renamed
    def on_moved(self, event):
        print(f"[{dt.now()}]Moved: {event.src_path} to {event.dest_path}")

if __name__ == "__main__":
    # Set the path to the folder you want to watch
    path = "/Volumes/FLAME_MEDIA/OUTPUT"  # Change this to your folder path
    
    event_handler = WatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    
    print(f"Now watching: {path}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching.")
    
    observer.join()
