"""
SmartWebSearch.CLI
~~~~~~~~~~~~

This module implements the Command Line Interface tool for the package.
"""

# Import the required modules
import SmartWebSearch as sws
from SmartWebSearch import ProgressStatusSelector as pss
import art
import time
from typing import Any, TypeAlias, Literal
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
import datetime
import os
import json

# Type Alias
SEARCH_MODES: TypeAlias = Literal['SEARCH', 'DEEPSEARCH']
SEARCH_DEPTHS: TypeAlias = Literal['MINIMAL', 'LOW', 'MEDIUM', 'HIGH']

# CLI Class
class CLI:
    """
    This class implements the Command Line Interface tool for the package.
    """

    # Constants

    # Line Types
    SINGLE_LINE: str = "--------------------------------------------------------------------------"
    DOUBLE_LINE: str = "=========================================================================="

    # White lines
    WHITE_LINE_LG: str = "\n\n\n\n\n"
    WHITE_LINE_MD: str = "\n\n\n"
    WHITE_LINE_SM: str = "\n"

    # CLI Settings

    # Tool Settings
    OPENAI_COMP_API_BASE_URL: str = None
    OPENAI_COMP_API_KEY: str = None
    OPENAI_COMP_API_MODEL: str = None
    TAVILY_API_KEY: str = None

    AI_MODEL: sws.AIModel = None
    WEB_SEARCH: sws.SmartWebSearch = None

    # Web Search Settings
    SEARCH_MODE: SEARCH_MODES = 'SEARCH'
    SEARCH_DEPTH: SEARCH_DEPTHS = 'LOW'

    # Configuration File Path
    CONFIG_FILE: str = os.path.join(os.path.dirname(sws.__file__), 'cli_config.json')

    # Messages
    MESSAGES: list[dict[str, Any]] = []

    @staticmethod
    def _setup():
        """
        Setup the Command Line Interface tool.

        Returns:
            None
        """

        # Start the setup process
        
        # Process 1/4 - OpenAI compatible API base URL
        print(CLI.WHITE_LINE_MD)
        print("<Process 1/4> What is your OpenAI compatible base URL?")
        openai_comp_api_base_url: str = input("Enter your base URL ----- [https://api.deepseek.com/chat/completions] >> ")
        openai_comp_api_base_url: str = openai_comp_api_base_url if openai_comp_api_base_url else "https://api.deepseek.com/chat/completions"
        print(f"[OK ✅] Current OpenAI compatible API base URL set to: '{openai_comp_api_base_url}'")

        # Process 2/4 - OpenAI compatible API Key
        print(CLI.WHITE_LINE_MD)
        print("<Process 2/4> What is your OpenAI compatible API key?")
        openai_comp_api_key: str = input("Enter your OpenAI compatible API key ----- >> ").strip()
        while not openai_comp_api_key:
            print("[ERROR ❌] OpenAI compatible API key is required!")
            openai_comp_api_key: str = input("Re-enter your OpenAI compatible API key ----- >> ").strip()
        print(f"[OK ✅] Current OpenAI compatible API key set to: '{openai_comp_api_key[:10]}...{openai_comp_api_key[-10:]}'")

        # Process 3/4 - OpenAI compatible API AI Model
        print(CLI.WHITE_LINE_MD)
        print("<Process 3/4> What is your OpenAI compatible model?")
        openai_comp_api_model: str = input("Enter your OpenAI compatible model ----- [deepseek-chat] >> ").strip()
        openai_comp_api_model: str = openai_comp_api_model if openai_comp_api_model else "deepseek-chat"
        print(f"[OK ✅] Current OpenAI compatible API model set to: '{openai_comp_api_model}'")

        # Process 4/4 - Tavily API key
        print(CLI.WHITE_LINE_MD)
        print("<Process 4/4> What is your Tavily API key?")
        tavily_api_key: str = input("Enter your Tavily API key ----- >> ").strip()
        while not tavily_api_key:
            print("[ERROR ❌] Tavily API key is required!")
            tavily_api_key: str = input("Re-enter your Tavily API key ----- >> ").strip()
        print(f"[OK ✅] Current Tavily API key set to: '{tavily_api_key[:10]}...{tavily_api_key[-10:]}'")

        # Checking the validity of the API keys
        print(CLI.WHITE_LINE_MD)
        print("<Checking> Checking the validity of the API keys ...")

        try:
            ai_model: sws.AIModel = sws.AIModel(openai_comp_api_key, openai_comp_api_model, openai_comp_api_base_url)
            sws.KeyCheck.check_openai_comp_api_key(ai_model)
            sws.KeyCheck.check_tavily_api_key(tavily_api_key)
        except sws.InvalidKeyError as e:
            print(f"[ERROR ❌] {e}")
            print(CLI.DOUBLE_LINE)

            print(CLI.WHITE_LINE_SM)

            print("Resetting the setup process ...")
            print(CLI.DOUBLE_LINE)

            print(CLI.WHITE_LINE_SM)

            CLI._setup()
            return
        
        print(f"[OK ✅] API keys have been verified successfully!")

        print(CLI.WHITE_LINE_MD)
        print(f"<Processing> Preparing for the tool and saving the API credentials ...")

        # Save the API keys
        CLI.OPENAI_COMP_API_BASE_URL = openai_comp_api_base_url
        CLI.OPENAI_COMP_API_KEY = openai_comp_api_key
        CLI.OPENAI_COMP_API_MODEL = openai_comp_api_model
        CLI.TAVILY_API_KEY = tavily_api_key

        # Initialize the AI model
        CLI.AI_MODEL = sws.AIModel(CLI.OPENAI_COMP_API_KEY, CLI.OPENAI_COMP_API_MODEL, CLI.OPENAI_COMP_API_BASE_URL)

        # Initialize the web search object
        CLI.WEB_SEARCH = sws.SmartWebSearch(CLI.TAVILY_API_KEY, CLI.AI_MODEL)

        # Save the API credentials to a configuration file
        with open(CLI.CONFIG_FILE, "w", encoding = "utf-8") as f:
            json.dump(
                {
                    "api_credentials": {
                        "openai_comp_api_base_url": CLI.OPENAI_COMP_API_BASE_URL,
                        "openai_comp_api_key": CLI.OPENAI_COMP_API_KEY,
                        "openai_comp_api_model": CLI.OPENAI_COMP_API_MODEL,
                        "tavily_api_key": CLI.TAVILY_API_KEY
                    }
                },
                f,
                indent = 4
            )

        # Show success message
        print(f"[OK ✅] API keys have been set successfully!")
        print(CLI.DOUBLE_LINE)

    def _info():
        """
        Print the tool info.

        Returns:
            None
        """

        # Print the tool info
        print(CLI.WHITE_LINE_LG)
        print(art.text2art(f'SmartWebSearch\nCLI', font='slant'))
        print(CLI.SINGLE_LINE)
        print("SmartWebSearch Command-Line Interface (CLI) Tool")
        print(f"Author: {sws.__author__}")
        print(f"Version: {sws.__version__}")
        print("Copyright (c) 2026 LIN WAI CHON")
        print(CLI.DOUBLE_LINE)

    @staticmethod
    def _mainloop():
        """
        Main loop of the Command Line Interface tool.

        Returns:
            None
        """

        # Create a function to stream the summary
        def stream(s: str):
            nonlocal full_text

            # Add a new line after the completion ended to separate the summaries and the debugging messages
            if s == sws.Summarizer.COMPLETION_ENDED:
                return

            # Update the text
            full_text += s

            # Update the live console
            live.update(Markdown(full_text))

        def status(s: sws._ProgressData):
            # Start the live console and print a single line when the summary starts to be generated
            if s.status == pss.CONCLUDING:
                live.start()
                print(CLI.SINGLE_LINE)
                print(CLI.WHITE_LINE_SM)

            # Show the progress
            if s.status == pss.STORMED:
                if 'tasks' in s.data:
                    print(f"[STORMED] Stormed {len(s.data['tasks'])} tasks ...")
                elif 'main_query' in s.data:
                    print(f"[STORMED] Stormed a main query and {len(s.data['auxiliary_queries'])} auxiliary queries ...")
                else:
                    print(f"[STORMED] Stormed {len(s.data['auxiliary_queries'])} auxiliary queries ...")

            if s.status == pss.SEARCHED:
                print(f"[SEARCHED] Searched {len(s.data['results'])} results for query '{s.data['query']}' ...")

            if s.status == pss.PARSED:
                print(f"[PARSED] Parsed all results for query '{s.data['query']}' ...")

            if s.status == pss.KL_BASE_CREATING:
                print(f"[KL_BASE_CREATING] Created knowledge base {s.data['current']}/{s.data['total']} (eta. {s.data['eta']}) ...")

            if s.status == pss.KL_BASE_CREATED:
                print(f"[KL_BASE_CREATED] Knowledge base set has been created ...")

        print(CLI.WHITE_LINE_LG)
        print(art.text2art("Search", font='slant'))
        print(CLI.DOUBLE_LINE)

        # Print help message
        print("Need help? Type /help to show the help message.")

        while True:
            # Set up the Rich console tools
            console = Console()
            live = Live(console=console, refresh_per_second = 10)

            full_text: str = ""

            # Add the progress listener
            CLI.WEB_SEARCH.progress.add_progress_listener(status)

            print(CLI.WHITE_LINE_SM)

            # Wait for user input
            u_prompt: str = input(f"[{CLI.SEARCH_MODE}{f' - {CLI.SEARCH_DEPTH}' if CLI.SEARCH_MODE == 'DEEPSEARCH' else ''}] >> ").strip()

            print(CLI.SINGLE_LINE)
            
            # Check if the user input is not empty
            if not u_prompt.strip():
                continue

            # Check if the user input is start with '/'
            if u_prompt.startswith('/'):
                # Check user input command
                cmd: str = u_prompt[1:].strip().lower()
                cmd_list: list[str] = cmd.split()

                # If the command is exit
                if cmd == 'exit':
                    break

                # Match the command
                CLI._command(cmd_list)

                # Continue the loop
                continue

            # Check if the user prompt less than 10 characters
            if len(u_prompt) < 10:
                print(f"[WARNING] Your prompt '{u_prompt}' is too short. Please enter a longer prompt.")
                continue

            # Start a search
            print(f"[SEARCHING] Searching for your prompt '{u_prompt}' in {CLI.SEARCH_MODE} mode ...")

            # Append the prompt to the messages
            CLI.MESSAGES.append(
                {
                    "role": "user",
                    "search_mode": CLI.SEARCH_MODE,
                    "content": u_prompt,
                    "timestamp": datetime.datetime.now().timestamp()
                }
            )

            # Start the live console
            live.start()

            # Search
            if CLI.SEARCH_MODE == 'SEARCH':
                content: str = CLI.WEB_SEARCH.search(u_prompt, stream)

            elif CLI.SEARCH_MODE == 'DEEPSEARCH':
                content: str = CLI.WEB_SEARCH.deepsearch(u_prompt, stream, CLI.SEARCH_DEPTH)

            # Stop the live console
            live.stop()

            print(CLI.WHITE_LINE_SM)
            print(CLI.DOUBLE_LINE)
            print(CLI.WHITE_LINE_SM)

            # Append the content to the messages
            CLI.MESSAGES.append(
                {
                    "role": "assistant",
                    "search_mode": CLI.SEARCH_MODE,
                    "content": content,
                    "timestamp": datetime.datetime.now().timestamp()
                }
            )

            # Remove the progress listener
            CLI.WEB_SEARCH.progress.remove_progress_listener(status)

    @staticmethod
    def _help():
        """
        Print the help message.

        Returns:
            None
        """

        print(CLI.WHITE_LINE_LG)
        print(art.text2art("Help", font='slant'))
        print("--- Commands & Usages `<> = Required, [] = Optional, () = Available Options` ---")
        print("> <prompt> - Start a new search in current search mode with the given prompt")
        print("> /help - Show the help message")
        print("> /search - Switch to search mode")
        print("> /deepsearch [depth (MINIMAL, LOW, MEDIUM, HIGH)] - Switch to deep search mode with the given depth")
        print("> /reset - Reset the CLI configuration and API credentials")
        print("> /save - Save the messages to a file (JSON)")
        print("> /cls - Clear the console")
        print("> /clear - Clear the console")
        print("> /exit - Exit the program")
        print(CLI.DOUBLE_LINE)

    @staticmethod
    def _save():
        """
        Save the messages to a file.

        Returns:
            None
        """

        # Save the messages to a file
        filename: str = f"messages-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"

        with open(filename, 'w', encoding = 'utf-8') as f:
            json.dump({
                "messages": CLI.MESSAGES,
                "timestamp": datetime.datetime.now().timestamp()
            }, f, indent = 4, ensure_ascii = False)
        
        print(f"[INFO] Messages have been saved to '{os.path.abspath(filename)}'")

    @staticmethod
    def _command(cmd_list: list[str]):
        """
        Match and run a command.

        Args:
            cmd_list (list[str]): The command list.

        Returns:
            None
        """

        # Match the command
        match cmd_list[0]:
            case 'help':
                # Print the help message
                CLI._help()

            case 'cls':
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')

            case 'clear':
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')

            case 'search':
                CLI.SEARCH_MODE = 'SEARCH'
                print(f"[INFO] Search mode has been set to '{CLI.SEARCH_MODE}'")

            case 'deepsearch':
                CLI.SEARCH_MODE = 'DEEPSEARCH'

                # Check if the user input has a depth
                if len(cmd_list) > 1:
                    # Match the depth
                    match cmd_list[1]:
                        case 'minimal':
                            CLI.SEARCH_DEPTH = 'MINIMAL'
                        case 'low':
                            CLI.SEARCH_DEPTH = 'LOW'
                        case 'medium':
                            CLI.SEARCH_DEPTH = 'MEDIUM'
                        case 'high':
                            CLI.SEARCH_DEPTH = 'HIGH'

                print(f"[INFO] Search mode has been set to '{CLI.SEARCH_MODE}' with depth '{CLI.SEARCH_DEPTH}'")

            case 'save':
                # Save the messages to a file
                CLI._save()

            case 'reset':
                # Check user input
                u_input: str = input("This process will reset the configuration file. Are you sure? (y/n) >> ").strip().lower()

                if u_input != 'y':
                    print("<Resetting> Reset process has been cancelled")
                    return

                # Print the reset message
                print("<Resetting> Resetting the setup process ...")

                # Remove the configuration file
                os.remove(CLI.CONFIG_FILE)

                # Run the setup
                CLI._setup()

            case _:
                print(f"[ERROR] Unknown command '{cmd_list[0]}'")

    @staticmethod
    def _goodbye():
        """
        Print the goodbye message.

        Returns:
            None
        """

        # Print the goodbye message
        print(CLI.WHITE_LINE_LG)
        print(art.text2art(f'Goodbye!', font='slant'))
        print(CLI.SINGLE_LINE)
        print("Thank you for using the SmartWebSearch CLI Tool!")
        print(CLI.SINGLE_LINE)

    @staticmethod
    def run():
        """
        Run the Command Line Interface tool.

        Returns:
            None
        """

        # Set up debugging mode to False
        sws.DebuggerConfiguration.DEBUGGING = False

        # Print the tool info
        CLI._info()

        # Wait for 1 seconds
        time.sleep(1)
        
        # Check if the configuration file exists
        if os.path.exists(CLI.CONFIG_FILE):
            print(CLI.WHITE_LINE_SM)

            print("<Loading> Loading the configuration file ...")
            print(CLI.DOUBLE_LINE)

            print(CLI.WHITE_LINE_SM)

            # Load the configuration file
            with open(CLI.CONFIG_FILE, "r", encoding = "utf-8") as f:
                cli_config: dict[str, Any] = json.load(f)

            # Checking the validity of the API keys
            print(CLI.WHITE_LINE_MD)
            print("<Checking> Checking the validity of the API keys ...")

            try:
                ai_model: sws.AIModel = sws.AIModel(
                    cli_config["api_credentials"]["openai_comp_api_key"],
                    cli_config["api_credentials"]["openai_comp_api_model"],
                    cli_config["api_credentials"]["openai_comp_api_base_url"]
                )
                sws.KeyCheck.check_openai_comp_api_key(ai_model)
                sws.KeyCheck.check_tavily_api_key(cli_config["api_credentials"]["tavily_api_key"])

                print(f"[OK ✅] API keys have been verified successfully!")

                print(CLI.WHITE_LINE_MD)
                print(f"<Processing> Preparing for the tool ...")

                # Save the API keys
                CLI.OPENAI_COMP_API_BASE_URL = cli_config["api_credentials"]["openai_comp_api_base_url"]
                CLI.OPENAI_COMP_API_KEY = cli_config["api_credentials"]["openai_comp_api_key"]
                CLI.OPENAI_COMP_API_MODEL = cli_config["api_credentials"]["openai_comp_api_model"]
                CLI.TAVILY_API_KEY = cli_config["api_credentials"]["tavily_api_key"]

                # Initialize the AI model
                CLI.AI_MODEL = sws.AIModel(CLI.OPENAI_COMP_API_KEY, CLI.OPENAI_COMP_API_MODEL, CLI.OPENAI_COMP_API_BASE_URL)

                # Initialize the web search object
                CLI.WEB_SEARCH = sws.SmartWebSearch(CLI.TAVILY_API_KEY, CLI.AI_MODEL)

                # Show success message
                print(f"[OK ✅] API keys have been set successfully!")
                print(CLI.DOUBLE_LINE)

            except sws.InvalidKeyError as e:
                print(f"[ERROR ❌] {e}")
                print(CLI.DOUBLE_LINE)

                print(CLI.WHITE_LINE_SM)

                print("<Resetting> Resetting the setup process ...")
                print(CLI.DOUBLE_LINE)

                print(CLI.WHITE_LINE_SM)

                CLI._setup()
        
        else:
            # Setup the CLI
            print(CLI.WHITE_LINE_LG)
            print(art.text2art(f'Setup', font='slant'))
            print(CLI.SINGLE_LINE)
            print("Welcome to the SmartWebSearch CLI Tool!")
            print("Let's set up the tool and get started!")
            print(CLI.SINGLE_LINE)

            # Wait for user input
            u_option: str = input("[S] Setup the tool, [Q] Quit the tool ----- [S] >> ").strip().lower()
            u_option: str = u_option if u_option else 's'

            # If the user input is 'q', quit the tool
            if u_option == 'q':
                CLI._goodbye()
                return
            
            # Run the setup process
            CLI._setup()

        # Run tool mainloop
        CLI._mainloop()

        # Print the goodbye message
        CLI._goodbye()