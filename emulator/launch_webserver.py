import os
import subprocess
import threading
import msvcrt  # Windows-specific module for keyboard input
import httpd
import check4redist

if check4redist.check_redist() == 0:
    os._exit(0)
# Call the check_config() function from httpd.py
httpd.check_config()

# Get the absolute path of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to httpd.exe
httpd_path = os.path.join(script_dir, 'files', 'apache24', 'bin', 'httpd.exe')

# Define the path to the Apache logs directory
logs_dir = os.path.join(script_dir, 'files', 'apache24', 'logs')

# Command to launch httpd.exe in a separate console window
launch_command = 'start "Apache Server" /D "{}" /B {}'.format(os.path.dirname(httpd_path), httpd_path)

# Flag to indicate if the ESC key has been pressed
exit_flag = threading.Event()

# Function to listen for the ESC key
def key_listener():
    while not exit_flag.is_set():
        if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:  # ESC key
            exit_flag.set()

try:
    # Start the key listener thread
    key_thread = threading.Thread(target=key_listener)
    key_thread.start()

    # Launch httpd.exe
    subprocess.Popen(launch_command, shell=True)
    print("Webserver started. Press ESC to exit.")

    # Wait for the key listener thread to finish
    key_thread.join()

    # Terminate httpd.exe process
    subprocess.call(["taskkill", "/F", "/IM", "httpd.exe"])

    print("Webserver and script terminated.")

except Exception as e:
    print("An error occurred:")
    print(str(e))
    print("Check the logs at: {}".format(logs_dir))
finally:
    exit_flag.set()  # Ensure the key listener thread is terminated
