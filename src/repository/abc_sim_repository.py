from abc import ABC, abstractmethod


class SimCardRepository(ABC):

    @abstractmethod
    def save_data(self, data: dict, filename: str) -> None:
        """
        Abstract method to save data to a specified file.

        Args:
            data (dict): The data to be saved (as a dictionary).
            filename (str): Path to the data file.

        Raises:
            NotImplementedError: This method must be implemented in concrete subclasses.
        """
        pass

    @abstractmethod
    def get_current_data(self, filename: str) -> dict:
        """
        Abstract method to retrieve the current data from a specified file.

        Args:
            filename (str): Path to the data file.

        Returns:
            dict: A dictionary containing the loaded data.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If the file content cannot be decoded as JSON.
        """
        pass

    @abstractmethod
    def read_current_sim_data(self, path: str) -> dict:
        """
        Abstract method to read simulation data from a specified path.

        Args:
            path (str): Path to the simulation data file.

        Returns:
            dict: A dictionary containing the simulation data.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If the file content cannot be decoded as JSON.
        """
        pass

    @abstractmethod
    def save_sim_data(self, current_sim: dict, path: str) -> None:
        """
        Save sim data to a specified path.

        Args:
            current_sim (dict): The current sim data to be saved.
            path (str): The path where the data should be saved.

        Returns:
            None

        """
        pass