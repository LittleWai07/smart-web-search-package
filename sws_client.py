logo: str = """

SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW                    WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW                    WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW                    WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSS                             WWWWWWWW                    WWWWWWWW       SSSSSSSS
SSSSSSSS                             WWWWWWWW                    WWWWWWWW       SSSSSSSS
SSSSSSSS                             WWWWWWWW                    WWWWWWWW       SSSSSSSS
SSSSSSSS                             WWWWWWWW                    WWWWWWWW       SSSSSSSS
SSSSSSSS                             WWWWWWWW                    WWWWWWWW       SSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
                      SSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW                             SSSSSSSS
                      SSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW                             SSSSSSSS
                      SSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW                             SSSSSSSS
                      SSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW                             SSSSSSSS
                      SSSSSSSS       WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW                             SSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWWWWWWWWWW    WWWWWWWWWWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWWWWWWWWW      WWWWWWWWWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS

==============================================================================================================

CCCCCCCCCCCC   LLL           IIIIIIIII
CCCCCCCCCCCC   LLL           IIIIIIIII
CCC            LLL              III
CCC            LLL              III
CCC            LLL              III
CCC            LLL              III
CCC            LLL              III
CCC            LLL              III
CCC            LLL              III
CCCCCCCCCCCC   LLLLLLLLLLL   IIIIIIIII
CCCCCCCCCCCC   LLLLLLLLLLL   IIIIIIIII

==============================================================================================================

"""

line: str = "\n==============================================================================================================\n"
singleline: str = "\n--------------------------------------------------------------------------------------------------------------\n"

# Imports dependencias
import requests, urllib3
import json, os
from typing import Literal, TypeAlias

# Set typealias
_SearchModes: TypeAlias = Literal["search", "deepsearch"]

# Set config file directory
config_file_dir: str = "C:/.swsconfig"

# Show logo
print(logo)

# Show client name and version
print("SmartWebSearch Client Version 1.0.0\n\n" + line)

# Show welcome message
print("Welcome to SmartWebSearch Client!!!\n" + line)

# Show Config file path
print("Config file path: " + config_file_dir + "/sws_config.json\n" + line)

# If the config file directory doesn't exist, create it
if not os.path.exists(config_file_dir):
    os.makedirs(config_file_dir, exist_ok = True)

# If the config file doesn't exist, create it
if not os.path.exists(config_file_dir + "/sws_config.json"):
    with open(config_file_dir + "/sws_config.json", "w", encoding = "utf-8") as f:
        json.dump({"host": None, "ts_key": None, "ds_key": None}, f, indent = 4)

# Get API key from config file
with open(config_file_dir + "/sws_config.json", "r", encoding = "utf-8") as f:
    config = json.load(f)

# If the API key is not set, get it from the user
if not (config["host"] and config["ts_key"] and config["ds_key"]):
    print("Setup Client\n" + line)

    while not config["host"]:
        config["host"] = input("Please enter your SmartWebSearch host (Default: 127.0.0.1:5000): ")
        if not config["host"]:
            config["host"] = "127.0.0.1:5000"

    while not config["ts_key"]:
        config["ts_key"] = input("Please enter your Tavily API key: ")

    while not config["ds_key"]:
        config["ds_key"] = input("Please enter your DeepSeek AI API key: ")

    # Save the API key to the config file
    with open("sws_config.json", "w", encoding = "utf-8") as f:
        json.dump(config_file_dir + config, f, indent = 4)

    print(line + "\nClient setup complete!\n" + line)

# Set search mode
search_mode: _SearchModes = "search"

def search():
    print(line + "\n" + """OOO  OOO   O   OO   OOO  O O
O    O    O O  O O  O    O O
OOO  OOO  OOO  OO   O    OOO
  O  O    O O  O O  O    O O
OOO  OOO  O O  O O  OOO  O O
    """)
    print("Mode: " + search_mode + "\n" + line)

    while True:
        # Get search prompt from user
        prompt = input(line + "\n" + "Please enter your search prompt (Type 'exit' to go back to the command prompt): ")

        # If the prompt is empty, continue the loop
        if not prompt.strip():
            continue

        # If the search mode is 'search', remind the user that the search process can take a few seconds to complete
        if search_mode == "search":
            print("Please wait, the search process can take a few seconds to complete...")

        # If the search mode is 'deepsearch', remind the user that the deepsearch process can take a few minutes to complete
        if search_mode == "deepsearch":
            print("Please wait, the deepsearch process can take a few minutes to complete...")

        # If the prompt is 'exit', exit the program
        if prompt == "exit":
            break

        # Send request to API
        try:
            response = requests.post(
                f"http://{config['host']}/{search_mode}",
                headers = {"Content-Type": "application/json"},
                json = {
                    "prompt": prompt,
                    "ts_key": config["ts_key"],
                    "ds_key": config["ds_key"]
                }
            )
        
        
            # Raise an exception if the request fails
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Print error message
            print(line + "\nAn HTTP error occurred: " + str(e) + "\n" + line)
            continue
        except requests.exceptions.ConnectionError as e:
            # Print error message
            print(line + "\nA connection error occurred, please check your internet connection, server running status and try again" + "\n" + line)
            continue

        # Print response
        print(line + "\n" + response.json()["summary"] + "\n" + line)

def help():
    print(line + "\nHelp: Available commands\n" + singleline)
    print("search - Switch to search mode\n")
    print("deepsearch - Switch to deepsearch mode\n")
    print("clear - Clear the screen\n")
    print("help - List available commands\n")
    print("exit - Exit the program\n" + line)

# Run search
search()

# Print help message
help()

while True:
    # Get command from user
    command = input(line + "\n" + "SWS > ")

    # If the command is 'exit', exit the program
    if command == "exit":
        break

    # If the command is 'search', change search mode to 'search'
    if command == "search":
        search_mode = "search"
        print(line + "\nSwitching to search mode...\n" + line)
        search()

    # If the command is 'deepsearch', change search mode to 'deepsearch'
    elif command == "deepsearch":
        search_mode = "deepsearch"
        print(line + "\nSwitching to deepsearch mode...\n" + line)
        search()

    # If the command is 'clear', clear the screen
    elif command == "clear":
        os.system("cls")

    # If the command is 'help', list available commands
    elif command == "help":
        help()

print(line + "\nGoodbye! Have a nice day!\n" + line)