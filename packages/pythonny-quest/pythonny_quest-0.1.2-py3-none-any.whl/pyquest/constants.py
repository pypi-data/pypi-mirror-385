# constants.py
from pathlib import Path
from pygments.token import Token

DATA_DIR = Path.home() / '.cache' / 'pyquest'
LOG_DIR = DATA_DIR / 'log'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = (LOG_DIR / __name__).with_suffix('.jsonlines')
STATUS_PATH = (DATA_DIR / 'status').with_suffix('.jsonlines')
MAX_STATUS_LINE_LEN = 1024
MAX_STATUS_FILE_LEN = 1024 * 16
token_colors = {
    Token.LightPurple: "#af87ff",
    Token.WarmYellow: "#ffd700",
    Token.Lightblue: "#5fd7ff",
    Token.Lightpurple: "#af87ff",
    Token.Lightgreen: "#87ff87",
    Token.Lime: "#afff00",
    Token.Darkyellow: "#ddb777",
    Token.Orange: "#ff8700",
    Token.Red: "#dd0000",
    Token.Blue: "#4444d7",
    Token.Green: "#22cc22",
    Token.Yellow: "#ffd787",
    Token.Grey: "#aaaaaa",
}

text_colors = {
    "lightblue": "\x1b[38;5;69m",
    "lightpurple": "\x1b[38;5;141m",
    "lightgreen": "\x1b[38;5;113m",
    "lime": "\x1b[38;5;154m",
    "darkyellow": "\x1b[38;5;220m",
    "orange": "\x1b[38;5;208m",
    "red": "\x1b[38;5;198m",
    "pink": "\x1b[38;5;213m",
    "magenta": "\x1b[38;5;206m",
    "tan": "\x1b[38;5;179m",
    "lighttan": "\x1b[38;5;180m",
    "yellow": "\x1b[38;5;226m",
    "green": "\x1b[38;5;34m",
    "blue": "\x1b[38;5;21m",
    "purple": "\x1b[38;5;91m",
    "purple_blue": "\x1b[38;5;63m",
    "lightgrey": "\x1b[38;5;250m",
    "grey": "\x1b[38;5;244m",
    "darkgrey": "\x1b[38;5;240m",
    "reset": "\x1b[0m",
}
