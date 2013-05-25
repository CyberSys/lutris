""" Non-blocking Gio Downloader  """
import time
from gi.repository import Gio, GLib, GObject


class Downloader():
    downloaded_bytes = 0
    total_bytes = 0
    time_elapsed = 0
    time_remaining = 0
    speed = 0

    def __init__(self, url, dest):
        self.remote = Gio.File.new_for_uri(url)
        self.local = Gio.File.new_for_path(dest)
        self.cancellable = Gio.Cancellable()
        self.progress = 0
        self.start_time = None

    def progress_callback(self, downloaded_bytes, total_bytes, _user_data):
        self.downloaded_bytes = downloaded_bytes
        self.total_bytes = total_bytes
        self.time_elapsed = time.time() - self.start_time
        self.speed = self.downloaded_bytes / self.time_elapsed or 1
        self.time_remaining = (total_bytes - downloaded_bytes) / self.speed
        self.progress = float(downloaded_bytes) / float(total_bytes)

    def cancel(self):
        self.cancellable.cancel()

    def download(self, job, cancellable, user_data):
        flags = Gio.FileCopyFlags.OVERWRITE
        self.remote.copy(self.local, flags, self.cancellable,
                         self.progress_callback, None)

    def start(self):
        GObject.threads_init()
        self.start_time = time.time()
        Gio.io_scheduler_push_job(self.download, None,
                                  GLib.PRIORITY_DEFAULT, self.cancellable)
