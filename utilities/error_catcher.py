import sys
import traceback


def custom_exception_handler(type, value, tb) :
    """
    Custom exception handler to print errors in red using ANSI escape codes.
    """
    RED = '\033[2;2;91m'  # Red color code
    DARKRED = '\033[31m'
    RESET = '\033[0m'  # Reset color code

    # Print the exception type and value in red
    print(f"{RED}An error occurred: ", end="")
    print("".join(traceback.format_exception_only(type, value)).strip( ) + RESET)

    # Optionally, print the full traceback
    print(DARKRED + "".join(traceback.format_tb(tb)) + RESET)


# Set the custom exception handler
sys.excepthook = custom_exception_handler