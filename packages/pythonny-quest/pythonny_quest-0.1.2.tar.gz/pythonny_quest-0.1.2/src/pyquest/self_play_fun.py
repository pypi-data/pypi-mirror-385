import logging
import os
import pexpect as pe
from pyte.screens import Screen
from pyte.streams import Stream
import re
import sys
import time
import select

log = logging.getLogger(__name__)

ROWS, COLS = 24, 80
EOLPAT = r'[\r\n]\n?'
VERSION_PATTERN = r'[.a-zA-Z0-9]{0,8}\s*'  # r'[\d]+[.]?[\d]+[.]?\d*'
INITIAL_PATTERN = r'^GNU Chess[ ]*(' + VERSION_PATTERN + r')\s*' + EOLPAT
MOVE_PATTERN = r'[Mm]y move is\s*:\s*([-_ a-zA-Z0-9]+)' + EOLPAT
RESIGN_PAT = r'^resign' + EOLPAT
PROMPT_PATTERN = r'([Ww]hite|[Bb]lack)\s*\((\d+)\)\s*:\s*'


def inputtimeout(text, timeout=10, default=''):
    stdin, stdout, stderr = select.select([sys.stdin], [], [], 10)
    if (stdin):
        return stdin
    return default


def start(cmd='gnuchess', pattern=INITIAL_PATTERN, rows=ROWS, cols=COLS):
    env = os.environ.copy()
    env.update({'LINES': str(rows), 'COLUMNS': str(cols)})
    process = pe.spawn(cmd, echo=False, encoding='utf-8', dimensions=(rows, cols), env=env)
    process.screen = Screen(COLS, ROWS)
    process.stream = Stream(process.screen)
    process.match_index = None
    process.match_index = process.expect(pattern)
    if process.match_index == 0:
        ver = None
        if process.match_index == 0:
            ver = tuple([int(i) for i in process.match.groups()[0].strip().split('.')])
            process.gnuchess_version = ver
    else:
        log.error(f'FAILED TO MATCH PATTERN: {pattern}\nException: {process.match_index}')

    return process


def play_game(
        cmd='gnuchess', rows=ROWS, cols=COLS,
        movepat=MOVE_PATTERN, promptpat=PROMPT_PATTERN, resignpat=RESIGN_PAT,
        timeout=1):
    hist = []
    i, turn = 0, 0
    color = 'White'

    board = start(cmd=cmd)
    lines = emulate_terminal(board)
    print(lines)

    hist.append(dict(i=i, color=color, match_index=board.match_index, turn=turn))

    while board.match_index == 0 and turn is not None and color is not None:
        board.match_index = None
        board.match_index = board.expect([promptpat, pe.EOF, pe.TIMEOUT])
        lines = emulate_terminal(board)
        print(lines)

        i, turn, move = 1, None, 'go'
        if board.match_index == 0:
            text = board.before
            resign_match = re.match(resignpat, text)
            if resign_match:
                print(f'!!!!!!!! {color.upper()} RESIGNED !!!!!')
                break

            move_match = re.match(movepat, text)
            if move_match:
                move = move_match.groups()[0]
            hist.append(
                dict(
                    i=i, color=color, match_index=board.match_index,
                    board_match=board.match, move_match=move_match, resign_match=resign_match,
                    turn=turn, move=move)
            )

            color, turn = board.match.groups()
            color = color
            turn = int(turn)
            # print(f'{color} ({turn}): go')
            # print(text)
            human = inputtimeout(f'Human, make a move! You have {timeout} sec: ', timeout=timeout)
            next_move = 'go'
            if human.strip():
                next_move = human.strip()
            board.sendline(next_move)
            # time.sleep(1)
        else:
            print(f'TIMEOUT OR EOF!!!\n{board.match_index}\n')
            break
    hist.append(dict(i=i, color=color, match_index=board.match_index,
                     board_match=board.match, move_match=move_match, resign_match=resign_match,
                     turn=turn, move=move, board=board))
    return hist


# black = pe.spawn('gnuchess')
# numblack = black.expect(r'Chess\s*')
# black.screen = Screen(NUMCOL, NUMROW)
# black.stream = Stream(black.screen)


def emulate_terminal(process, clean=True):
    """ Send raw output to pyte.Stream and get the emulated output from pyte.Screen.

    *Reset* the display at each call, so we don't get the same emulated output twice.
    Pyte emulates the whole terminal so it will return us ROWS rows of COLS columns, each one completed with spaces.
    Optionally strip whitespace on the right and any empty line at the end.
    """
    process.stream.feed(process.before + process.after)
    lines = process.screen.display
    process.screen.reset()

    if clean:
        lines = (line.rstrip() for line in lines)
        lines = (line for line in lines if line)

    return '\n'.join(lines)


def print_status(process, turn=0, color='White'):
    print()
    print('=' * 30 + f'{color} board' + '=' * 30)
    print(process.before + process.after)
    print('=' * 80)


def update_terminal(process):
    process.screen.write(process.before)
    process.screen.write(process.after)


if __name__ == '__main__':
    games = []
    games.append(play_game())


# def play_round(white, black, next_turn=1, pattern=PATTERN):
#     global white, black
#     print_status(white, black)
#     white.expect(pattern)
#     # moves = [i, white_move, black_move] + list(white.match.groups()) + list(black.match.groups()) \
#     #     + list(map(bytes.decode,
#     #                (white.before, white.after, black.before, black.after)))
#     white_move, white_color, turn = [x.decode() for x in white.match.groups()]
#     white_move = white_move.strip() or 'go'
#     print(f'{white_color}_move: {white_move}')
#     assert white_color.strip().lower() == 'White', \
#         f'ERROR: Expected "White". Got "{white_color}"!'
#     assert turn or white_move == 'go', \
#         f'ERROR: White should move first! turn={turn}, white_move={white_move}'
#     assert next_turn == int(turn.strip())
#     white.sendline(white_move)
#     white.expect(pattern)
#     print(white.before + white.after)

#     # black.expect(r'\s*([a-zA-Z0-9]{0,6})\s*([Ww]hite|[Bb]lack)\s*\(\d+\)\s*:\s*')
#     # black.sendline(black_move)
#     # move, color = [x.decode() for x in white.match.groups()]
#     return next_turn + 1
