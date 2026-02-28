"""
SmartWebSearch.Progress
~~~~~~~~~~~~

This module implements the progress for the web searching module.
"""

# Import the required modules
from typing import Any, TypeAlias, Literal, Callable
from datetime import datetime

# Type Alias
_ProgressStatus: TypeAlias = Literal['IDLE', 'STORMING', 'STORMED', 'SEARCHING', 'SEARCHED', 'PARSING', 'PARSED', 'KL_BASE_CREATING', 'KL_BASE_CREATED', 'KL_BASE_MATCHING', 'KL_BASE_MATCHED', 'CONCLUDING', 'CONCLUDED', 'PART_COMPLETED', 'COMPLETED', 'REQUEST_TIMEOUT']

# Progress Classes
class ProgressStatusSelector:
    """
    A class representing the status of a web searching operation.
    """

    # Constants
    IDLE: _ProgressStatus = 'IDLE'
    STORMING: _ProgressStatus = 'STORMING'
    STORMED: _ProgressStatus = 'STORMED'
    SEARCHING: _ProgressStatus = 'SEARCHING'
    SEARCHED: _ProgressStatus = 'SEARCHED'
    PARSING: _ProgressStatus = 'PARSING'
    PARSED: _ProgressStatus = 'PARSED'
    KL_BASE_CREATING: _ProgressStatus = 'KL_BASE_CREATING'
    KL_BASE_CREATED: _ProgressStatus = 'KL_BASE_CREATED'
    KL_BASE_MATCHING: _ProgressStatus = 'KL_BASE_MATCHING'
    KL_BASE_MATCHED: _ProgressStatus = 'KL_BASE_MATCHED'
    CONCLUDING: _ProgressStatus = 'CONCLUDING'
    CONCLUDED: _ProgressStatus = 'CONCLUDED'
    PART_COMPLETED: _ProgressStatus = 'PART_COMPLETED'
    COMPLETED: _ProgressStatus = 'COMPLETED'
    REQUEST_TIMEOUT: _ProgressStatus = 'REQUEST_TIMEOUT'

class _ProgressData:
    """
    A class representing the data of a web searching operation.
    """

    def __init__(self, status: _ProgressStatus = 'IDLE', message: str = None, data: Any = None, progress: float = None, timestamp: datetime = None) -> None:
        """
        Initializes a new instance of the _ProgressData class.

        Args:
            status (_ProgressStatus) = 'IDLE': The status of the progress.
            message (str) = None: The message to display. Defaults to None.
            data (Any) = None: The data to display. Defaults to None.
            progress (float) = None: The progress of the operation. Defaults to None. Range: [0.0, 1.0].
            timestamp (datetime) = datetime.now(): The timestamp of the progress. Defaults to current datetime.
        
        Returns:
            None
        """

        self.__status: _ProgressStatus = status
        self.__message: str = message
        self.__data: Any = data
        self.__progress: float = progress
        self.__timestamp: datetime = timestamp if timestamp else datetime.now()

    def __str__(self) -> str:
        """
        Returns the string representation of the _ProgressData class.

        Returns:
            str: The string representation of the _ProgressData class.
        """

        return f"_ProgressData(status='{self.__status}', message='{self.__message}', data='{self.__data}', progress='{self.__progress}', timestamp='{self.__timestamp}')"

    @property
    def status(self) -> _ProgressStatus:
        """
        Returns the status of the progress.

        Returns:
            _ProgressStatus: The status of the progress.
        """
        return self.__status
    
    @property
    def message(self) -> str:
        """
        Returns the message of the progress.

        Returns:
            str: The message of the progress.
        """
        return self.__message
    
    @property
    def data(self) -> Any:
        """
        Returns the data of the progress.

        Returns:
            Any: The data of the progress.
        """
        return self.__data
    
    @property
    def progress(self) -> float:
        """
        Returns the progress of the progress.

        Returns:
            float: The progress of the progress.
        """
        return self.__progress
    
    @property
    def timestamp(self) -> datetime:
        """
        Returns the timestamp of the progress.

        Returns:
            datetime: The timestamp of the progress.
        """
        return self.__timestamp

class Progress:
    """
    A class representing the progress of a web searching operation.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the Progress class.
        
        Returns:
            None
        """

        # Initialize the class attributes
        self.__current_progress: _ProgressData = _ProgressData()
        self.__progress_listeners = []
    
    def add_progress_listener(self, listener: Callable[[_ProgressStatus], None]) -> None:
        """
        Adds a listener to the progress of a web searching operation.

        Args:
            listener (Callable[[_ProgressStatus], None]): The callback function to add.
        
        Returns:
            None
        """

        # Add the listener to the list of listeners
        self.__progress_listeners.append(listener)

    def remove_progress_listener(self, listener: Callable) -> None:
        """
        Removes a listener from the progress of a web searching operation.

        Args:
            listener (Callable[]): The callback function to remove.
        
        Returns:
            None
        """

        # Remove the listener from the list of listeners
        self.__progress_listeners.remove(listener)

    def _update_progress(self, status: _ProgressStatus, message: str = None, data: Any = None, progress: float = None, timestamp: datetime = None) -> None:
        """
        Updates the progress of a web searching operation.

        Args:
            status (_ProgressStatus): The status of the progress.
            message (str, optional): The message to display. Defaults to None.
            data (Any, optional): The data to display. Defaults to None.
            progress (float, optional): The progress of the operation. Defaults to None. Range: [0.0, 1.0].
            timestamp (datetime, optional): The timestamp of the progress. Defaults to current datetime.
        
        Returns:
            None
        """

        # Update the progress
        self.__current_progress: _ProgressData = _ProgressData(status, message, data, progress, timestamp)

        # Call the listeners
        for listener in self.__progress_listeners:
            listener(self.__current_progress)