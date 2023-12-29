import logging
import logging.handlers
import configparser
import sys
import queue
import re

from config import read_config

config = read_config()
loglevel = config["log_level"]
logtofile = config["log_to_file"]


class SpecificDebugFilter(logging.Filter) :
    def filter(self, record) :
        # Define a regular expression pattern that matches your specific log messages
        pattern = re.compile(r"\('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', (\d+)\): Received data with length  - [0-9a-fA-F ]+")
        # Check if the log record matches the specific pattern
        if pattern.match(record.getMessage( )) :
            return False  # Exclude this specific message from the console
        return True  # Include all other messages


class ProgressBarFilter(logging.Filter) :
    def filter(self, record) :
        if config.get("enable_progress_bar", False) and record.name == "GCFCHKSUM" or record.name == "converter" :
            return False  # Do not log to console for this logger if progress bar is enabled
        else :
            return True


class ColoredFormatter(logging.Formatter) :
    COLORS = {
        "MODULE" : "\033[93m",  # yellow
        "LEVEL"  : "\033[90m",  # Aqua for level indicator
        "WARNING": "\033[93m",  # Yellow
        "INFO": "\033[32;10m",     # Green
        "DEBUG": "\033[94m",    # Blue
        "CRITICAL": "\033[91m", # Red
        "ERROR": "\033[91m",    # Red
        "EXCEPTION":"\033[31",  # Dark Red for Exceptions
        "TIME":"\033[37m",
        "RESET": "\033[0m"     # Reset
    }

    def formatException(self, exc_info):
        """
        Format and color the exception information.
        """
        exception_text = super(ColoredFormatter, self).formatException(exc_info)
        return f"{self.COLORS['EXCEPTION']}{exception_text}{self.COLORS['RESET']}"

    def formatTime(self, record, datefmt=None):
        formatted_time = super(ColoredFormatter, self).formatTime(record, datefmt)
        return f"{self.COLORS['TIME']}{formatted_time}{self.COLORS['RESET']}"

    def format(self, record) :
        levelname = record.levelname
        original_msg = record.msg
        record.asctime = f"{self.COLORS['TIME']}{record.asctime}{self.COLORS['RESET']}"
        record.name = f"{self.COLORS['MODULE']}{record.name}{self.COLORS['RESET']}"
        record.levelname = f"{self.COLORS['LEVEL']}{record.levelname}{self.COLORS['RESET']}"

        record.msg = f"{self.COLORS['TIME']}%s{self.COLORS['RESET']}" % record.asctime
        formatted = super( ).format(record)
        record.msg = original_msg
        if levelname in self.COLORS :
            record.msg = f"{self.COLORS[levelname]}{record.msg}{self.COLORS['RESET']}"
        return super( ).format(record)


def init_logger() :
	if logtofile.lower() == "true":
		# Create handlers for files and console
		fh = logging.handlers.RotatingFileHandler('logs\\emulator_debug.log', maxBytes=20000000, backupCount=10)
		fh.setLevel(logging.DEBUG)  # Debug and higher (includes INFO, WARNING, ERROR, CRITICAL)

		fh2 = logging.handlers.RotatingFileHandler('logs\\emulator_info.log', maxBytes=20000000, backupCount=5)
		fh2.setLevel(logging.INFO)  # Info and higher (includes WARNING, ERROR, CRITICAL)

		er = logging.handlers.RotatingFileHandler('logs\\emulator_error.log', maxBytes=20000000, backupCount=2)
		er.setLevel(logging.WARNING)  # Warning and higher (includes ERROR, CRITICAL)

	ch = logging.StreamHandler(sys.stdout)
	colored_formatter = ColoredFormatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

	level = getattr(logging, loglevel.split('.')[-1], logging.INFO)
	ch.setLevel(level)

	# Common formatter
	formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
	if logtofile.lower() == "true":
		fh.setFormatter(formatter)
		fh2.setFormatter(formatter)
		er.setFormatter(formatter)
	# ch.setFormatter(formatter)
	ch.setFormatter(colored_formatter)
	ch.addFilter(SpecificDebugFilter( ))
	ch.addFilter(ProgressBarFilter( ))  # Apply the new filter

	# Create a queue and QueueHandler
	log_queue = queue.Queue(-1)
	queue_handler = logging.handlers.QueueHandler(log_queue)

	# Create a root logger
	root = logging.getLogger()
	root.setLevel(logging.DEBUG)

	# Attach ONLY the QueueHandler to the root logger
	root.addHandler(queue_handler)

	# Create and start a QueueListener
	# QueueListener will distribute logs to the file and console handlers
	listener = logging.handlers.QueueListener(log_queue, fh, fh2, er, ch)
	listener.start()