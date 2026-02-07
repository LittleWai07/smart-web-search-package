"""
SmartWebSearch.RAGTool
~~~~~~~~~~~~

This module implements the Debugger Tool for the package.
"""

# Import the required modules
import json, os, sys, shutil, re
from typing import Any, TypeAlias, Literal

# Type Alias
_DebugType: TypeAlias = Literal['INFO', 'WARNING', 'ERROR', 'FILE']

# Configuration Class
class DebuggerConfiguration:
    """
    DebuggerConfiguration class for the Debugger Tool.
    """

    # Whether to enable debugging
    DEBUGGING: bool = False

    # Functions
    def clear_debug_files() -> None:
        """
        Clear all debug files in the current directory.

        Returns:
            None
        """

        # Get all files in the current directory
        files: list[str] = os.listdir()

        # Loop through the files
        for file in files:
            # Check if the file is a debug file
            if file.startswith("debug-"):
                # Delete the file
                os.remove(file)

    # Run the clear_debug_files function
    clear_debug_files()

# Functions
def show_debug(*values: tuple[Any], type: _DebugType = 'INFO') -> None:
    """
    Print the values to the console if DEBUGGING is True.
    
    Args:
        *values (tuple[Any]): The values to print.
        type (_DebugType) = 'INFO': The type of debug message.

    Returns:
        None
    """

    # Print the values if DEBUGGING is True
    if DebuggerConfiguration.DEBUGGING:
        print(f'[DEBUGGER] <{type}>', *values)

def create_debug_file(filename: str, ext: str, content: str) -> None:
    """
    Create a debug file with the given filename and content.

    Args:
        filename (str): The name of the file to create.
        ext (str): The extension of the file to create.
        content (str): The content to write to the file.

    Returns:
        None
    """

    # If not debugging, return
    if not DebuggerConfiguration.DEBUGGING: return

    # Replace all spaces in the filename to dash
    filename: str = filename.replace(" ", "-")

    # Replace all underscores in the filename to dash
    filename: str = filename.replace("_", "-")

    # Create the directory if it doesn't exist
    if os.path.dirname(filename):
        os.makedirs(os.path.dirname(filename), exist_ok = True)

    # Write the content to the file
    with open(f"debug-{filename}.{ext}", "w", encoding = "utf-8") as f:
        f.write(content)

    # Show debug message
    show_debug(f"Created debug file: 'debug-{filename}.{ext}', content length: {len(content)}", type = 'FILE')