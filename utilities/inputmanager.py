import msvcrt
import os
import threading


def start_watchescape_thread():
    def watchescape_thread():
        while True:
            if ord(msvcrt.getch()) == 27:
                os._exit(0)

    thread2 = threading.Thread(target=watchescape_thread)
    thread2.daemon = True
    thread2.start()