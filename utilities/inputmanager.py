import msvcrt
import os
import threading


def start_watchescape_thread():
    def watchescape_thread():
        escape_key_ord = ord('\x1b')  # Escape key ASCII value
        while True:
            if ord(msvcrt.getch()) == escape_key_ord:
                os._exit(0)

    thread2 = threading.Thread(target = watchescape_thread)
    thread2.daemon = True
    thread2.start()