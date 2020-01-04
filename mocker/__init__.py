import os
import colorama
import logging
import sys

__version__ = '0.0.1'

__doc__ = """Mocker.

Usage:
  mocker pull <name>[<tag>]
  mocker (-h | --help)
  mocker --version  
  
Options:
  -h --helppp     Show this screen.
  --version       Show version.
"""

_base_dir_ = os.path.join(os.path.expanduser('~'), 'mocker')


class ColorizingStreamHandler(logging.StreamHandler):
    color_map = {
        logging.DEBUG: colorama.Style.DIM + colorama.Fore.CYAN,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Back.RED,
    }

    def __init__(self, stream, color_map=None):
        logging.StreamHandler.__init__(self,
                                       colorama.AnsiToWin32(stream).stream)
        if colorama is not None:
            self.color_map = color_map

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            parts = message.split('\n', 1)
            parts[0] = self.colorize(parts[0], record)
            message = '\n'.join(parts)
        return message

    def colorize(self, message, record):
        try:
            return (self.color_map[record.levelno] + message +
                    colorama.Style.RESET_ALL)
        except KeyError:
            return message


log = logging.getLogger()
handler = ColorizingStreamHandler(sys.stdout)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)
