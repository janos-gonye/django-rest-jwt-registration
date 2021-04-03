import threading
import time


def interval(callback, delay):
    def _inner():
        callback()
        time.sleep(delay)
        _inner()
    thread = threading.Thread(target=_inner, daemon=True)
    thread.start()
