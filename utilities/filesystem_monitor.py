import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utilities import converter


class BaseFileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            self.handle_file(event.src_path)

    def handle_file(self, file_path):
        # To be implemented in subclass
        raise NotImplementedError

class GCFFileHandler(BaseFileEventHandler):
    def handle_file(self, file_path):
        if file_path.endswith('.gcf'):
            self.neutergcf(file_path)

    def neutergcf(self, file_path):
        print(f"Neutering GCF file: {file_path}")
        if self.wait_until_file_is_ready(file_path):
            converter.convertgcf(file_path)  # Assuming convertgcf accepts the file path as an argument
        else:
            print(f"File {file_path} was not ready for processing.")

    @staticmethod
    def wait_until_file_is_ready(file_path, retries=3, delay=2):
        """Wait for the file to be fully copied or written."""
        for _ in range(retries):
            if not os.path.isfile(file_path):
                return False  # File does not exist

            try:
                with open(file_path, 'rb') as file:
                    return True  # Successfully opened the file
            except IOError:
                time.sleep(delay)  # Wait for a while before retrying
        return False

class DirectoryMonitor:
    def __init__(self, directory, event_handler):
        self.directory = directory
        self.event_handler = event_handler
        self.observer = Observer()

    def start(self):
        self.observer.schedule(self.event_handler, self.directory, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()




"""class GCFConvertMonitorThread(threading.Thread):
    def __init__(self, directory, interval=1):
        super().__init__()
        self.directory = directory
        self.interval = interval
        self.processed_files = set()

    def run(self):
        while True:
            try:
                current_files = set(os.listdir(self.directory))
                new_files = current_files - self.processed_files
                for file in new_files:
                    if file.endswith('.gcf'):  # Assuming .gcf files need to be processed
                        converter.convertgcf()
                        self.processed_files.add(file)
                self.processed_files = self.processed_files & current_files
                time.sleep(self.interval)
            except Exception as e:
                print(f"Error in FileMonitorThread: {e}")"""