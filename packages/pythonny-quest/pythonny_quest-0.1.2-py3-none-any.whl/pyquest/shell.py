from IPython import start_ipython, get_ipython, embed
from IPython.terminal.prompts import Prompts
from IPython.terminal.ipapp import load_default_config
# from IPython.terminal.interactiveshell import TerminalInteractiveShell
from pygments.token import Token
from pyquest.constants import token_colors
from pyquest.utils import cprint
from pprint import pprint
import logging
import importlib
import readline  # noqa


log = logging.getLogger()

shell = None

goal_num, hint_num = 0, 0

# FIXME: make this a table with 3 fields/columns in local Sqlite cache and remote Supabase DB
quest = dict(
    status=dict(
        points=0,
        grade='F',
        found_help=0,
        ran_help=0,
        found_hidden=[],
    ),
    # Miniquests
    task=[
        '1: What is the full path to your current working directory where files will be saved.',
        '2: What files are in your "current working directory"?.',
        '3: Find and run the function you use to get help on any function in Python.',
        '4: Find and display the contents of as many hidden iPython variables as you can find.',
    ],
    answer=[
        'pwd',
        'ls',
        'help()',
        r'_.*',
    ],
    hint=[
        [
            'All shell and python commands are short (2-5 characters) and in all lowercase',
            'Lowercase acronym for print working directory',
            'Lowercase TLA (Three Letter Acronym) for "print working directory" that starts with "p"'
        ],
        [
            'Abbreviation for "list"',
            'Lowercase TLA (Two Letter Abbreviation) for the word list',
        ],
        [
            '4-letter word (not RTFM)',
            'The command is one of the words in the text description of this task',
        ],
        [
            'Hidden variables start with an `_` character',
            'in an iPython console you can hit the TAB character after typing something to get auto-complete hints',
        ],
    ]
)


def get_hint(increment=False):
    global quest, goal_num, hint_num
    hints = quest['hint'][goal_num]
    text = hints[hint_num]
    hint_num = (hint_num + int(increment)) % len(hints)
    return text


def get_goal(increment=False):
    global quest, goal_num, hint_num
    goals = quest['task']
    text = goals[goal_num]
    ans = quest['answer'][goal_num]
    cmd = get_history()
    cmd = cmd.replace("get_ipython().run_line_magic('", '')
    cmd = cmd.replace("', '')", '')
    increment = increment or (ans == cmd)
    if increment:
        hint_num = 0
    # print(len(h))
    goal_num = min(goal_num + int(increment), len(goals))
    return text


def get_goal_hint(increment=False):
    global quest, goal_num, hint_num
    goals = quest['task']
    cmd = get_history()
    cmd = cmd.replace("get_ipython().run_line_magic('", '')
    cmd = cmd.replace("', '')", '')
    ans = quest['answer'][goal_num]
    increment = increment or (ans == cmd)
    if increment:
        hint_num = 0
    # print(len(h))
    goal_num = min(goal_num + int(increment), len(goals))
    goal_text = goals[goal_num]
    hints = quest['hint'][goal_num]
    hint_text = hints[hint_num]
    hint_num = (hint_num + int(increment)) % len(hints)
    return goal_text, hint_text


def get_history():
    # Get the current IPython instance
    ip = get_ipython()

    if ip is not None:
        # Access input history
        input_history = ip.history_manager.input_hist_parsed

        # Get specific history entries
        for i, cmd in enumerate(input_history[-10:], 1):  # Last 10 commands
            # print(f"[{i}]: {cmd}")
            pass

        # # Or access raw input history
        # raw_history = ip.history_manager.input_hist_raw

        return str(input_history[-1])
    else:
        # print("Not in an IPython session")
        log.warning('get_history() before any user input!')
        return ''
        # , None


class QuestPrompt(Prompts):
    """ Custom iPython Quest Prompt """
    # def __init__(self, shell):
    # def vi_mode(self): ... return ''
    # def current_line(self) -> int:
    # def in_prompt_tokens(self):
    # def _width(self):
    # def continuation_prompt_tokens(self, width=None, *, lineno=None, wrap_count=None):
    # def rewrite_prompt_tokens(self):
    # def out_prompt_tokens(self):

    def in_prompt_tokens(self, cli=None):
        goal_text, hint_text = get_goal_hint()
        return [
            # (Token.Yellow, f"# {get_history()}\n"),
            (Token.Yellow, f"# {goal_text}\n"),
            (Token.Gray, f"# {hint_text}\n"),
            (Token.Green, ">>> ")]


class Shell:
    """ iPython adventures

    Commands:
      - help: Show this help message
      - docs: Open browser to show Workbench Documentation
      - config: Show the current Config
      - status: Show the current Status
      - log_(debug/info/important/warning): Set the Workbench log level
      - exit: Close the shell session and exit to the parent shell

    """

    def __init__(self):
        # if not self.config:
        #     # Invoke Onboarding Procedure
        #     onboard()

        # commands that are auto-executed without parens
        self.commands = dict(
            #            help=self.help,
            status=self.print_status,
            # quest=self.show_quest,
            log_debug=self.log_debug,
            log_info=self.log_info,
            log_warning=self.log_warning,
            log=logging.getLogger(),
            pprint=importlib.import_module("pprint").pprint,
        )

    def start(self):
        """Start the enhanced IPython shell (Pythonny Quest)"""
        cprint("green", "\nWelcome to the Pythonny Quest!")

        # Load the default IPython configuration
        config = load_default_config()
        # # Don't automatically call functions entered without parentheses
        # config.TerminalInteractiveShell.autocall = 2
        config.TerminalInteractiveShell.prompts_class = QuestPrompt
        config.TerminalInteractiveShell.highlighting_style_overrides = token_colors
        config.TerminalInteractiveShell.banner1 = ""

        # Merge custom commands and globals into the namespace
        locs = self.commands.copy()  # Copy the custom commands
        locs.update(globals())  # Merge with global namespace

        # Start IPython with the config and commands in the namespace
        start_ipython(["--no-tip", "--theme", "linux"], user_ns=locs, config=config)

    def show_config(self):
        cprint("yellow", "\nConfig:")
        cprint("lightblue", f"Path: {self.cm.site_config_path}")
        config = self.cm.get_all_config()
        for key, value in config.items():
            cprint(["lightpurple", "\t" + key, "lightgreen", value])

    # def spinner_start(self, text: str, color: str = "lightpurple") -> Spinner:
    #     spinner = Spinner(color, text)
    #     spinner.start()  # Start the spinner
    #     return spinner

    def print_status(self):
        """Show current progress and scores on learning quest"""
        status_data = self.get_status()

        cprint("yellow", "\nStatus:")
        pprint(status_data)
        return status_data

    @ staticmethod
    def log_debug():
        logging.getLogger().setLevel(logging.DEBUG)

    @ staticmethod
    def log_info():
        logging.getLogger().setLevel(logging.INFO)

    @ staticmethod
    def log_warning():
        logging.getLogger().setLevel(logging.WARNING)


def main():
    shell = Shell()
    shell.start()
    embed()
    return shell


# Start the shell when running the script
if __name__ == "__main__":
    main()
