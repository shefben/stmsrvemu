import sys
import curses

class CursesStdout:
    def __init__(self, window):
        self.window = window

    def write(self, text):
        self.window.addstr(text)
        self.window.refresh()
        sys.__stdout__.write(text)



def main(stdscr):
    # Initialize curses
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    # Redirect stdout to CursesStdout
    sys.stdout = CursesStdout(stdscr)


# Call the main function with curses.wrapper
#ben note: put this in the launcher main
curses.wrapper(main)