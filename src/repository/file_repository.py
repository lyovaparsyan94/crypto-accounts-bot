import json

from config import configs
from logs.aws_logger import awslogger
from repository.abc_sim_repository import SimCardRepository


class UserSimDataRepository(SimCardRepository):
    def save_data(self, data: dict, filename: str = configs.dir_configs.PATH_TO_SAVE) -> None:
        """
        Saves data to a specified file in JSON format.

        Args:
            data (dict): The data to be saved (as a dictionary).
            filename (str, optional): Path to the data file. Defaults to configs.dir_configs.PATH_TO_SAVE.

        Raises:
            PermissionError: If the file cannot be written due to permission issues.
        """
        try:
            with open(filename, "w") as file:
                json.dump(data, file, indent=2)
        except PermissionError:
            raise PermissionError(f"Permission denied. Cannot write to file '{filename}'.")

    def get_current_data(self, filename: str = configs.dir_configs.PATH_TO_SAVE) -> dict:
        """
        Retrieves the current data from a specified file.

        Args:
            filename (str, optional): Path to the data file. Defaults to configs.dir_configs.PATH_TO_SAVE.

        Returns:
            dict: A dictionary containing the loaded data.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If the file content cannot be decoded as JSON.
        """
        try:
            with open(filename) as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{filename}' not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON data from '{filename}'. Check the file format.")

    def read_current_sim_data(self, path: str = configs.dir_configs.PATH_OF_SIM_JSON) -> dict:
        """
        Reads the contents of a JSON file containing current SIM data.

        Args:
            path (str, optional): The path to the JSON file. Defaults to "PATH_OF_SIM_JSON".

        Returns:
            dict: The current SIM data as a dictionary.

        Notes:
            - The JSON file should contain a dictionary with keys: "operation_id", "received_number", and "country".
        """
        try:
            with open(path) as file:
                current_number_info = json.load(file)
                return current_number_info
        except FileNotFoundError:
            awslogger.log_critical(f"File '{path}' not found. Please make sure the file exists.")
            return {}

    def save_sim_data(self, current_sim: dict, path: str = configs.dir_configs.PATH_OF_SIM_JSON) -> None:
        """
        Saves the current SIM data (operation ID, received phone number, and country) to a JSON file.

        Args:
            current_sim (dict): A dictionary containing the current SIM data.
            path (str, optional): The path to the JSON file. Defaults to "current_sim.json".

        Returns:
            None
        """
        with open(path, 'w') as file:
            json.dump(current_sim, file, indent=4)
