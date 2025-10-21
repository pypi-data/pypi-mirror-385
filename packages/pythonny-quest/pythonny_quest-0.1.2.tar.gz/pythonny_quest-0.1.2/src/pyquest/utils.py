from collections import abc
import copy
from datetime import datetime
from fuzzywuzzy import process as fuzzy
import itertools
import json
import logging
import math
from pathlib import Path
import pandas as pd
from pyquest.constants import text_colors, token_colors  # noqa
from pyquest.constants import LOG_PATH
import sys
import threading
import time


def cprint(*args):
    """
    Print text in color. Supports either a single color and text or a list of color-text pairs.

    Args:
         A single color and text or a list of color-text pairs.
         For example: cprint('red', 'Hello') or cprint(['red', 'Hello', 'green', 'World'])
    """
    if isinstance(args[0], list):
        args = args[0]
    # Iterate over the arguments in pairs of color and text
    for i in range(0, len(args), 2):
        print(f"{text_colors[args[i]]}{args[i + 1]}{text_colors['reset']}", end=" ")
    print()  # Print a newline at the end


def status_lights(status_colors: list[str]):
    """
    Create status lights (circles) in color.

    Args:
        status_colors: A list of status colors (e.g. ['red', 'green', 'yellow']).

    Returns:
        A string representation of colored status lights.
    """
    circle = "●"  # Unicode character for a filled circle
    return "".join(f"{text_colors[color]}{circle}{text_colors['reset']}" for color in status_colors)


class Spinner:
    def __init__(self, color, message="Loading..."):
        """
        Initialize the Spinner object.

        Args:
            color: The color of the spinner.
            message: The message to display beside the spinner.
        """
        self.done = False
        self.message = message
        self.color = color
        self.thread = threading.Thread(target=self.spin)

    def _write(self, text):
        """Write text to stdout and flush."""
        sys.stdout.write(text)
        sys.stdout.flush()

    def _hide_cursor(self):
        """Hide the terminal cursor."""
        self._write("\033[?25l")

    def _show_cursor(self):
        """Show the terminal cursor."""
        self._write("\n\033[?25h")

    def spin(self):
        """Display a multi-spinner animation until stopped."""
        frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"  # Frames used for each spinner
        done_frame = "⠿⠿⠿⠿"  # Frames to show on completion

        # Create four separate cycle iterators for the spinners
        spinners = [itertools.cycle(frames) for _ in range(4)]

        # Initialize each spinner with staggered positions for visual effect
        for i, spinner in enumerate(spinners):
            for _ in range(i * 2):  # Stagger each spinner by 2 frames
                next(spinner)

        self._hide_cursor()
        while not self.done:
            # Construct the spinner display from each staggered spinner
            spinner_display = "".join(next(spinner) for spinner in spinners)
            self._write(f"\r{text_colors[self.color]}{self.message} {text_colors['darkyellow']}{spinner_display}")
            time.sleep(0.1)  # Control the speed of spinner animation

        # Display the "done" frame when completed
        self._write(f"\r{text_colors[self.color]}{self.message} {text_colors['lightgreen']}{done_frame}")
        self._show_cursor()

    def start(self):
        """Start the spinner in a separate thread."""
        self.thread.start()

    def stop(self):
        """Stop the spinner and wait for the thread to finish."""
        self.done = True
        self.thread.join()  # Ensure the spinner thread is fully stopped


log = logging.getLogger()


def is_serializable_type(obj):
    """ True if object is a built-in type that will work with json.dumps(obj)
    >>> [is_serializable_type(x) for x in [0, 1, None, '', float('nan'), -1.5, False, tuple(), set(), dict()]]
    [True, True, True, True, True, True, True, True, True, True]
    """
    return (
        obj.__class__.__module__ == 'builtins'
        or obj is None
    )


def dictify(obj, ignore_class_names=('Session',), ignore_startswith='_', ignore_endswith='_'):
    """ Recursively convert lists and dicts to built-in types serializable by json.dumps()

    >>> d = dict(a=1)
    >>> d[2] = (2, 'two')
    >>> d[None] = frozenset(['nan'])
    >>> d[float('-inf')] = None
    >>> dictify(d)
    {'a': 1, 2: [2, 'two'], None: [nan], -inf: None}
    >>> json.dumps(dictify(d))
    '{"a": 1, "2": [2, "two"], "null": [NaN], "-Infinity": null}'
    >>> dictify({Path.cwd(): Path.home()}) == {str(Path.cwd()): str(Path.home())}
    True
    """
    if isinstance(obj, (int, float)):
        return obj
    if isinstance(obj, Path):
        return str(obj)
    if callable(getattr(obj, 'isoformat', None)):
        return obj.isoformat()
    if obj is None:
        return obj
    if isinstance(obj, abc.Mapping):
        return {dictify(k): dictify(v) for k, v in obj.items() if not (
            str(k).startswith(ignore_startswith) or str(k).endswith(ignore_endswith) or v.__class__.__name__ in ignore_class_names
        )}
    if isinstance(obj, (list, tuple, set, frozenset)):  # or callable(getattr(obj, '__iter__', None)):
        return [dictify(x) for x in obj]
    if isinstance(obj, bytes):
        obj = obj.decode()
    if isinstance(obj, str):
        try:
            obj = float(obj)
            if obj == int(obj):
                return int(obj)
            return obj
        except (TypeError, ValueError) as err:
            log.debug(f'{obj} cannot be converted to an int or float: {err}')
            return obj
    if not hasattr(obj, '__dict__'):
        return str(obj)

    # Use obj.__dict__ attribute (vars(obj)) to serialize user-defined classes
    d = dict()
    for k, v in vars(obj).items():
        if str(k).startswith(ignore_startswith) or str(k).endswith(ignore_endswith) or v.__class__.__name__ in ignore_class_names:
            continue
        d[k] = dictify(v)
    return d


class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs in JSON format"""

    def format(self, record):
        # Create the log entry dictionary
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'pathname': record.pathname,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        extra_data = dictify(getattr(record, 'extra_data', None) or {})
        if isinstance(extra_data, dict):
            log_entry.update(extra_data)
        else:
            log_entry.update(dict(extra_data=extra_data))

        return json.dumps(log_entry, ensure_ascii=False)


class ModuleLineFormatter(logging.Formatter):
    """Custom formatter for stderr with module and line info"""

    def format(self, record):
        # Format: [LEVEL] module:line - message
        return f"[{record.levelname}] {record.module}:{record.lineno} - {record.getMessage()}"


def setup_logging(
    name=__name__,
    log_file=LOG_PATH,
    log_level=logging.INFO,
    file_log_level=logging.DEBUG,
    stderr_log_level=logging.INFO


):
    """
    Set up logging with JSON format to file and module:line format to stderr

    Args:
        log_file: Path to the log file
        log_level: Overall logging level
        file_log_level: Logging level for file handler
        stderr_log_level: Logging level for stderr handler
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create log directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # File handler with JSON formatting
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_log_level)
    file_handler.setFormatter(JSONFormatter())

    # Stderr handler with module:line formatting
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(stderr_log_level)
    stderr_handler.setFormatter(ModuleLineFormatter())

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stderr_handler)

    return logger


def test_logger(log_path=LOG_PATH.with_suffix('.log.test')):
    """ Example usage and logger tests """
    logger = setup_logging(
        name=__name__,
        log_file=log_path,
        log_level=logging.DEBUG,
        file_log_level=logging.DEBUG,
        stderr_log_level=logging.INFO
    )

    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("Application started successfully")
    logger.warning("This is a warning message")
    logger.error("An error occurred")

    # Test logging with extra data (for JSON)
    logger.info("User action", extra={'extra_data': {
        'user_id': 12345,
        'action': 'login',
        'ip_address': '192.168.1.1'
    }})

    # Test exception logging
    try:
        result = 1 / 0  # noqa
    except ZeroDivisionError:
        logger.exception("Intentional divide-by-zero error occurred")

    # Example of getting a named logger for a specific module
    module_logger = logging.getLogger(__name__)
    module_logger.info("This message includes the module name")

    print("\nLogging tests complete!")
    print(f"Check the '{log_path}' file for JSON formatted logs")
    print("Check stderr output above for module:line formatted logs")


def fuzzy_get(possible_keys, approximate_key, default=None, similarity=0.6, tuple_joiner='|',
              key_and_value=False, dict_keys=None):
    r"""Find the closest matching key in a dictionary (or element in a list)

    For a dict, optionally retrieve the associated value associated with the closest key

    Notes:
      `possible_keys` must have all string elements or keys!
      Argument order is in reverse order relative to `fuzzywuzzy.process.extractOne()`
        but in the same order as get(self, key) method on dicts

    Arguments:
      possible_keys (dict): object to run the get method on using the key that is most similar to one within the dict
      approximate_key (str): key to look for a fuzzy match within the dict keys
      default (obj): the value to return if a similar key cannote be found in the `possible_keys`
      similarity (float): fractional similiarity between the approximate_key and the dict key
        (0.9 means 90% of characters must be identical)
      tuple_joiner (str): Character to use as delimitter/joiner between tuple elements.
        Used to create keys of any tuples to be able to use fuzzywuzzy string matching on it.
      key_and_value (bool): Whether to return both the key and its value (True) or just the value (False).
        Default is the same behavior as dict.get (i.e. key_and_value=False)
      dict_keys (list of str): if you already have a set of keys to search,
        this will save this funciton a little time and RAM

    See Also:
      get_similar: Allows nonstring keys and searches object attributes in addition to keys

    Examples:

    >>> fuzzy_get({'seller': 2.7, 'sailor': set('e')}, 'sail') == set(['e'])
    True
    >>> fuzzy_get({'seller': 2.7, 'sailor': set('e'), 'camera': object()}, 'SLR')
    2.7
    >>> fuzzy_get({'seller': 2.7, 'sailor': set('e'), 'camera': object()}, 'I') == set(['e'])
    True
    >>> fuzzy_get({'word': tuple('word'), 'noun': tuple('noun')}, 'woh!', similarity=.3, key_and_value=True)
    ('word', ('w', 'o', 'r', 'd'))
    >>> fuzzy_get({'word': tuple('word'), 'noun': tuple('noun')}, 'woh!', similarity=.9, key_and_value=True)
    (None, None)
    >>> fuzzy_get({'word': tuple('word'), 'noun': tuple('noun')}, 'woh!', similarity=.9,
    ...           default='darn :-()', key_and_value=True)
    (None, 'darn :-()')
    >>> possible_keys = ('alerts astronomy conditions currenthurricane forecast forecast10day geolookup history ' +
    ...                  'hourly hourly10day planner rawtide satellite tide webcams yesterday').split()
    >>> fuzzy_get(possible_keys, "cond")
    'conditions'
    >>> fuzzy_get(possible_keys, "Tron")
    'astronomy'
    >>> import numpy as np
    >>> df = pd.DataFrame(np.arange(6*2).reshape(2,6), columns=('alpha','beta','omega','begin','life','end'))
    >>> fuzzy_get(df, 'beg')  # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    0    3
    1    9
    Name: begin, dtype: int...
    >>> fuzzy_get(df, 'get')
    >>> fuzzy_get(df, 'et')[1]
    np.int64(7)
    """
    dict_obj = copy.copy(possible_keys)
    if not isinstance(dict_obj, (abc.Mapping, pd.DataFrame, pd.Series)):
        dict_obj = dict((x, x) for x in dict_obj)

    fuzzy_key, value = None, default
    if approximate_key in dict_obj:
        fuzzy_key, value = approximate_key, dict_obj[approximate_key]
    else:
        strkey = str(approximate_key)
        if approximate_key and strkey and strkey.strip():
            # print 'no exact match was found for {0} in {1} so preprocessing keys'.format(approximate_key, dict_obj.keys())
            if any(isinstance(k, (tuple, list)) for k in dict_obj):
                dict_obj = dict((tuple_joiner.join(str(k2) for k2 in k), v) for (k, v) in dict_obj.items())
                if isinstance(approximate_key, (tuple, list)):
                    strkey = tuple_joiner.join(approximate_key)
            # fuzzywuzzy requires that dict_keys be a list (sets and tuples fail!)
            dict_keys = list(set(dict_keys if dict_keys else dict_obj))
            if strkey in dict_keys:
                fuzzy_key, value = strkey, dict_obj[strkey]
            else:
                strkey = strkey.strip()
                if strkey in dict_keys:
                    fuzzy_key, value = strkey, dict_obj[strkey]
                else:
                    fuzzy_key_scores = fuzzy.extractBests(strkey, dict_keys,
                                                          score_cutoff=min(max(similarity * 100.0 - 1, 0), 100),
                                                          limit=6)
                    if fuzzy_key_scores:
                        fuzzy_score_keys = []
                        # add length similarity as part of score
                        for (i, (k, score)) in enumerate(fuzzy_key_scores):
                            fuzzy_score_keys += [(score * math.sqrt(len(strkey)**2
                                                                    / float((len(k)**2 + len(strkey)**2) or 1)), k)]
                        fuzzy_score, fuzzy_key = sorted(fuzzy_score_keys)[-1]
                        value = dict_obj[fuzzy_key]
    if key_and_value:
        if key_and_value in ('v', 'V', 'value', 'VALUE', 'Value'):
            return value
        return fuzzy_key, value
    else:
        return value


def fuzzy_get_value(obj, approximate_key, default=None, **kwargs):
    """ Like fuzzy_get, but assume the obj is dict-like and return the value without the key

    Notes:
      Argument order is in reverse order relative to `fuzzywuzzy.process.extractOne()`
        but in the same order as get(self, key) method on dicts

    Arguments:
      obj (dict-like): object to run the get method on using the key that is most similar to one within the dict
      approximate_key (str): key to look for a fuzzy match within the dict keys
      default (obj): the value to return if a similar key cannote be found in the `possible_keys`
      similarity (str): fractional similiarity between the approximate_key and the dict key
        (0.9 means 90% of characters must be identical)
      tuple_joiner (str): Character to use as delimitter/joiner between tuple elements.
        Used to create keys of any tuples to be able to use fuzzywuzzy string matching on it.
      key_and_value (bool): Whether to return both the key and its value (True) or just the value (False).
        Default is the same behavior as dict.get (i.e. key_and_value=False)
      dict_keys (list of str): if you already have a set of keys to search, this will save this funciton
        a little time and RAM

    Examples:
      >>> fuzzy_get_value({'seller': 2.7, 'sailor': set('e')}, 'sail') == set(['e'])
      True
      >>> fuzzy_get_value({'seller': 2.7, 'sailor': set('e'), 'camera': object()}, 'SLR')
      2.7
      >>> fuzzy_get_value({'seller': 2.7, 'sailor': set('e'), 'camera': object()}, 'I') == set(['e'])
      True
      >>> fuzzy_get_value({'word': tuple('word'), 'noun': tuple('noun')}, 'woh!', similarity=.3)
      ('w', 'o', 'r', 'd')
      >>> import numpy as np
      >>> df = pd.DataFrame(np.arange(6*2).reshape(2,6), columns=('alpha','beta','omega','begin','life','end'))
      >>> fuzzy_get_value(df, 'life')[0], fuzzy_get(df, 'omega')[0]
      (np.int64(4), np.int64(2))
    """
    dict_obj = dict(obj)
    try:
        return dict_obj[list(dict_obj.keys())[int(approximate_key)]]
    except (ValueError, IndexError):
        pass
    return fuzzy_get(dict_obj, approximate_key, key_and_value=False, **kwargs)


def fuzzy_get_tuple(dict_obj, approximate_key, dict_keys=None, key_and_value=False, similarity=0.6, default=None):
    """Find the closest matching key and/or value in a dictionary (must have all string keys!)"""
    return fuzzy_get(dict(('|'.join(str(k2) for k2 in k), v) for (k, v) in dict_obj.items()),
                     '|'.join(str(k) for k in approximate_key), dict_keys=dict_keys,
                     key_and_value=key_and_value, similarity=similarity, default=default)


def get_module_logger(name=None):
    """Get a logger for a specific module"""
    if name is None:
        name = __name__
    return logging.getLogger(name)
