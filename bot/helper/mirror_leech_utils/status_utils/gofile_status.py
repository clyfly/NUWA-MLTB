from time import time
from logging import getLogger

from .... import bot_loop
from ....core.config_manager import Config
from ...ext_utils.bot_utils import get_readable_file_size, MirrorStatus, get_readable_time

LOGGER = getLogger(__name__)

class GofileStatus:
    def __init__(self, listener, uploader, gid):
        self._listener = listener
        self._uploader = uploader
        self._gid = gid
        self._start_time = time()

    def gid(self):
        return self._gid

    def progress(self):
        # Gofile API doesn't provide progress, so we'll return a placeholder
        return "0%"

    def speed(self):
        # Gofile API doesn't provide speed, so we'll return a placeholder
        return "0 B/s"

    def name(self):
        return self._listener.name

    def size(self):
        return get_readable_file_size(self._listener.size)

    def eta(self):
        # Gofile API doesn't provide ETA, so we'll return a placeholder
        return "N/A"

    def status(self):
        if self._uploader.is_uploading:
            return MirrorStatus.STATUS_UPLOADING
        return MirrorStatus.STATUS_QUEUEDL

    def processed_bytes(self):
        if not self._uploader.is_uploading:
            return self._listener.size
        return 0

    def listener(self):
        return self._listener

    def cancel_task(self):
        LOGGER.info(f"Cancelling Upload: {self._listener.name}")
        if self._uploader:
            self._uploader.cancel_upload()
        self._listener.on_upload_error("Upload cancelled by user!")