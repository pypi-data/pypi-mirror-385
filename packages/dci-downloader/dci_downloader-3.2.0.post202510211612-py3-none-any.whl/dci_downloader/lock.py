import os
import fcntl
import sys


if sys.version_info[0] == 3:
    LOCK_IO_ERROR = BlockingIOError  # noqa: F821
else:
    LOCK_IO_ERROR = IOError


class LockError(Exception):
    pass


class file_lock(object):
    lock_fd = None

    def __init__(self, file_path):
        lock_fd = open(file_path, "a+")
        try:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except LOCK_IO_ERROR:
                raise LockError("Couldn't lock %s" % file_path)
            self.lock_fd = lock_fd
        except Exception:
            lock_fd.close()
            raise

    def __enter__(self):
        return self.lock_fd

    def __exit__(self, type, value, traceback):
        try:
            os.remove(self.lock_fd.name)
        except OSError:
            print("Strange issue can't remove %s (OSError)" % self.lock_fd.name)
        fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
        self.lock_fd.close()
        self.lock_fd = None
