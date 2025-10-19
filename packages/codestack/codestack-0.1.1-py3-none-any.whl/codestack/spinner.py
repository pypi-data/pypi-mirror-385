import itertools
import sys
import threading
import time
import os

def spinner(message="codestack is building your project"):
    """
    Displays a simple spinner animation in the console while the model is generating code.
    Call the returned stop() function to stop the spinner.
    """
    stop_flag = {"running": True}

    def spin():
        for c in itertools.cycle(["|", "/", "-", "\\"]):
            if not stop_flag["running"]:
                break
            sys.stdout.write(f"\r{message}... {c}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r \n Build complete!\n")

    t = threading.Thread(target=spin)
    t.daemon = True
    t.start()

    def stop():
        time.sleep(0.2)
        stop_flag["running"] = False
        t.join()

    return stop