""" Maintain a jsonlines log of player status, and a read-only compressed json file of Quest defnitions.

>>> from tempfile import gettempdir
>>> path = Path(gettempdir()) / 'pyquest_deleteme_status_tests.jsonlines'
>>> path.open('w').close()
>>> s = read_status(path=path)
>>> type(s)
<class 'dict'>
>>> dicts_equal(s, INITIAL_STATUS)
True
>>> progress = dict(points=1, questnum=1, completed_tasks=['0.1', '0.2', '0.3'])
>>> new_status = update_status(progress, path=path)
>>> s.update(progress)
>>> dicts_equal(new_status, s)
True
"""
from pyquest.constants import STATUS_PATH, MAX_STATUS_LINE_LEN, MAX_STATUS_FILE_LEN
from pyquest.util import dictify
import json
import jsonlines
from pathlib import Path
import os

import logging
from tempfile import gettempdir
log = logging.getLogger()


SEEK_END = 2
# SEEK_BEGIN = 0

# FIXME: make this a table with 3 fields/columns in local Sqlite cache and remote Supabase DB
INITIAL_STATUS = dictify(dict(
    status_path=STATUS_PATH,
    module_path=__file__,
    points=0,
    weeknum=0,
    pace=0,
    questnum=0,
    tasknum=0,
    completed_tasks=[],
))


def dicts_equal(d1, d2):
    """ Compare dicts as lists of 2-tuples """
    return list(d1.items()) == list(d2.items())


def read_status(path=STATUS_PATH, default=None):
    """ Get the latest status on the current environment (one player per OS user) """
    if default is None:
        default = INITIAL_STATUS.copy()
    default = dictify(default)
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)
    elif path.is_file():
        obj = read_last_jsonline(path)
        if isinstance(obj, dict) and len(obj):
            return obj
    with jsonlines.open(path, 'a') as fout:
        # print(default, fout)
        fout.write(default)
    return default


def write_status(status, path=STATUS_PATH):
    """ Get the latest status on the current environment (one player per OS user) """
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)
    with jsonlines.open(path, 'a') as fout:
        fout.write(status)
    return status


def read_last_jsonline(
        path=STATUS_PATH,
        chunk_size=MAX_STATUS_LINE_LEN, max_file_len=MAX_STATUS_FILE_LEN, default_type=dict):
    """ Return the last line of a jsonlines file, after parsing the line of json to create a Python object """
    with Path(path).open("rb") as fin:
        file_len = fin.seek(0, os.SEEK_END)
        if not file_len:
            return default_type()
        fin.seek(min(max(file_len - chunk_size - 2, 0), file_len))
        text_bytes = fin.read()
    lines = [txt.strip() for txt in text_bytes.decode().splitlines()]
    if len(lines) >= 1:
        try:
            return json.loads(lines[-1])
        except json.JSONDecodeError:
            log.warning(f'No valid jsonlines found: {path}')
            return str(lines[-1])
    # elif len(lines) == 1:
    #     log.warning(f'Only found one jsonline in {path}.')
    #     return json.loads(lines[-1])
    elif file_len == 0 or len(lines) == 0 or len(lines[-1]) == 0:
        log.warning(f'Could not find any valid jsonlines in {path}. file_len={file_len}. len(lines)={len(lines)}')
        return default_type()
    chunk_size = min(chunk_size * 2, file_len)
    # Limit recursion depth by stopping exponential fallback (file length increase)
    if chunk_size > max_file_len:
        raise RuntimeError(
            f'Unable to find last line for {path}.'
            'max_file_len={max_file_len}, file_len={file_len}, max_line_len={max_line_len}'
        )
    # if max_line_len < max_file_len and file_len < max_line_len:
    return read_last_jsonline(path=path, chunk_size=chunk_size, max_file_len=max_file_len, default_type=default_type)


def update_status(status=None, path=STATUS_PATH):
    if status is None:
        status = dict()
    previous_status = read_status()
    previous_status.update(status)
    write_status(previous_status, path=path)
    return previous_status
