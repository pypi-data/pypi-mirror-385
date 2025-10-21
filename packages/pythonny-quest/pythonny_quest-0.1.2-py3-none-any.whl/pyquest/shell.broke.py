from IPython import start_ipython, embed
from IPython.terminal.prompts import Prompts
from IPython.terminal.ipapp import load_default_config
from pygments.token import Token
from pyquest.constants import token_colors
from pyquest.utils import cprint
from pprint import pprint
import logging
import importlib
import readline  # noqa

shell = None

goal_num, hint_num = 0, 0

# FIXME: make this a table with 3 fields/columns in local Sqlite cache and remote Supabase DB
quest = dict(
    status=dict(
        points=0,
        grade='F',
        goal_num=0,
        hint_num=0,
    ),
    goal=dict(
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
    hint=[
        [
            'All shell and python commands are short (2-5 characters) and in all lowercase',
            'Lowercase acronym for print working directory',
            'Lowercase TLA(Three Letter Acronym) for print working directory that starts with "p"'
        ],
        [
            'Abbreviation for "list"',
            'Lowercase TLA (Two Letter Abbreviation) for the word list'
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


def get_hint(goal_num=goal_num, hint_num=hint_num):
    global quest
    quest['status']['goal_num'] = goal_num = goal_num or quest['status']['goal_num']
    return quest['hint'][goal_num][hint_num]


class QuestPrompt(Prompts):
    """ Custom iPython Quest Prompt """

    def in_prompt_tokens(self, cli=None):
        return [
            (Token.Gray, f"# {get_hint()}\n"),
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
        """Start the enhanced IPython shell"""
        cprint("green", "\nWelcome to the iPython adventure game!")

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

    def print_status(self):
        """Show current progress and scores on learning quest"""
        status_data = self.get_status()

        cprint("yellow", "\nStatus:")
        pprint(status_data)
        return status_data

    @staticmethod
    def log_debug():
        logging.getLogger("pyquest").setLevel(logging.DEBUG)

    @ staticmethod
    def log_info():
        logging.getLogger("pyquest").setLevel(logging.INFO)

    @ staticmethod
    def log_warning():
        logging.getLogger("pyquest").setLevel(logging.WARNING)


def main():
    shell = Shell()
    shell.start()
    embed()
    return shell


# Start the shell when running the script
if __name__ == "__main__":
    main()
