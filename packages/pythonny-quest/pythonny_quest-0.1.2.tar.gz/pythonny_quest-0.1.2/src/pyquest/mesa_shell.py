""" Customized IPython.start_ipython embedded shell """
from IPython import start_ipython
from IPython.terminal.prompts import Prompts
from IPython.terminal.ipapp import load_default_config
from pygments.token import Token
from pprint import pprint
import logging
import importlib
import webbrowser
import readline  # noqa

from pyquest.utils import cprint, Spinner

prompt_styles = {
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


shell = None

# FIXME: make this a table with 3 fields/columns in local Sqlite cache and remote Supabase DB
quest = dict(
    status=dict(
        points=0,
        grade='F',
        step=0,
    ),
    goal=dict(
        found_help=0,
        ran_help=0,
        found_hidden=[],
    ),
    # Miniquests
    hint=[
        '1: What is the full path to your current working directory - the default place where any files will be saved.',
        '2: What files are in your "current working directory" - the default directory or folder where files will be saved.',
        '3: Find and run the function you use to get help on any function in Python.',
        '4: Find and display the contents of as many hidden iPython variables as you can find.',
    ],
)


def get_hint(step_num=0):
    global quest
    quest['status']['step_num'] = step_num = step_num or quest['status']['step_num']
    return quest['hint'][step_num]


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
        return [
            (Token.Gray, f">>> # {get_hint()}\n"),
            (Token.Green, ">>> ")]  # + aws_profile_prompt


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
        # # Check the Workbench config
        # self.cm = ConfigManager()
        # if not self.cm.config_okay():
        #     # Invoke Onboarding Procedure
        #     onboard()

        # Our Metadata Object pull information from the Cloud Platform
        self.meta = None
        self.meta_status = "DIRECT"

        # Perform AWS connection test and other checks
        self.commands = dict(
            help=self.help,
            docs=self.doc_browser,
            status=self.print_status,
            quests=self.pipelines,
            log_debug=self.log_debug,
            log_info=self.log_info,
            log_warning=self.log_warning,
            config=self.show_config,
            log=logging.getLogger("mesa"),
            # pd=importlib.import_module("pandas"),
            pprint=importlib.import_module("pprint").pprint,
        )

    def start(self):
        """Start the enhanced IPython shell"""
        cprint("magenta", "\nWelcome to the iPython adventure game!")

        # Load the default IPython configuration
        config = load_default_config()
        # # Don't automatically call functions entered without parentheses
        # config.TerminalInteractiveShell.autocall = 2
        config.TerminalInteractiveShell.prompts_class = QuestPrompt
        config.TerminalInteractiveShell.highlighting_style_overrides = prompt_styles
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

    def help(self, *args, **kwargs):
        """Custom help command to replace help() with self.__doc__ otherwise fall back to help(whatever) """
        if args:
            help(*args, **kwargs)
        else:
            cprint("lightblue", self.__doc__)

    def spinner_start(self, text: str, color: str = "lightpurple") -> Spinner:
        spinner = Spinner(color, text)
        spinner.start()  # Start the spinner
        return spinner

    @staticmethod
    def doc_browser():
        """Open a browser and start the Dash app and open a browser."""
        url = "https://supercowpowers.github.io/workbench/"
        webbrowser.open(url)

    def print_status(self):
        """Show current progress and scores on learning quest"""
        spinner = self.spinner_start("Chatting with AWS:")
        status_data = self.request_status()
        spinner.stop()

        cprint("yellow", "\nStatus:")
        pprint(status_data)
        return status_data

    def incoming_data(self):
        return self.meta.incoming_data()

    def glue_jobs(self):
        return self.meta.etl_jobs()

    def data_sources(self):
        return self.meta.data_sources()

    def feature_sets(self, details: bool = False):
        return self.meta.feature_sets(details=details)

    def models(self, details: bool = False):
        return self.meta.models(details=details)

    def endpoints(self):
        return self.meta.endpoints()

    def pipelines(self):
        return self.meta.pipelines()

    @staticmethod
    def log_debug():
        logging.getLogger("workbench").setLevel(logging.DEBUG)

    @staticmethod
    def log_info():
        logging.getLogger("workbench").setLevel(logging.INFO)

    @staticmethod
    def log_warning():
        logging.getLogger("workbench").setLevel(logging.WARNING)


if __name__ == "__main__":
    shell = Shell()
    shell.start()
