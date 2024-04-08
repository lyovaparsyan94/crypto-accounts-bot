import asyncio
import json

from config import configs
from logs.aws_logger import awslogger
from pyonlinesim import OnlineSMS


class AsyncOnlineSimHandler:

    def __init__(self, api_token: str) -> None:
        """
        Initializes an instance of AsyncOnlineSimHandler.

        Args:
            api_token (str): The API token for OnlineSim service.
        """
        self.__api_token = api_token
        self.operation_id = None
        self.received_phone_number = None

    async def __get_balance(self) -> str:
        """
        Retrieves the account balance from the SMS service.

        Returns:
            str: The account balance as a string.
        """
        async with OnlineSMS(api_key=self.__api_token) as client:
            result = await client.get_balance()
            return result

    async def __get_service_info(self) -> dict:
        """
        Retrieves service information from the SMS service.

        Returns:
            dict: A dictionary containing service details.
                - Key: Service name (e.g., "Amazon")
                - Value: Service ID, available numbers, price, and service name
        """
        async with OnlineSMS(api_key=self.__api_token) as client:
            countryes = await client.get_services(country=configs.aws_configs.ONLINE_COUNTRY_CODE)
            for service in countryes.services:
                if service.service == configs.aws_configs.ONLINE_SIM_SERVICE:
                    awslogger.log_info(
                        f'ID: {service.id} | Available Numbers: {service.count} | Service: {service.service} | Price: {service.price}')
                    return {f"{configs.aws_configs.ONLINE_SIM_SERVICE}": service.id, 'available_numbers': service.count,
                            'service_name': configs.aws_configs.ONLINE_SIM_SERVICE}

    async def __order_number(self, service: str = configs.aws_configs.ONLINE_SIM_SERVICE,
                             country: int = configs.aws_configs.ONLINE_COUNTRY_CODE) -> str:
        """
        Orders a phone number using the OnlineSMS API.

        Args:
            service (str, optional): The service type. Defaults to "ONLINE_SIM_SERVICE".
            country (int, optional): The country code. Defaults to "ONLINE_COUNTRY_CODE".

        Returns:
            str: The received phone number.
        """
        async with OnlineSMS(api_key=self.__api_token) as client:
            order = await client.order_number(service=service, country=country, number=True)
            if order:
                received_number = order.number
                self.operation_id = order.operation_id
                self.received_phone_number = received_number
                current_sim = {
                    "operation_id": order.operation_id,
                    "received_number": order.number,
                    "country": order.country,
                }
                self.save_sim_data(current_sim)
                return received_number

    def save_sim_data(self, current_sim: dict, path: str = configs.dir_configs.PATH_OF_SIM_JSON) -> None:
        """
        Saves the current SIM data (operation ID, received phone number, and country) to a JSON file.

        Args:
            current_sim (dict): A dictionary containing the current SIM data.
            path (str, optional): The path to the JSON file. Defaults to "current_sim.json".

        Returns:
            None
        """
        with open(f'{path}', 'w') as file:
            json.dump(current_sim, file, indent=4)

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
            with open(f"{path}") as file:
                current_number_info = json.load(file)
                return current_number_info
        except FileNotFoundError:
            awslogger.log_critical(f"File '{path}' not found. Please make sure the file exists.")
            return {}

    async def check_current_active_sim(self, operation_id: int) -> dict[str, str] | None:
        """
        Checks if the specified operation ID corresponds to an active phone number.

        Args:
            operation_id (int): The operation ID to check.

        Returns:
            Optional[Dict[str, str]]: A dictionary containing information about the active number
                (phone, country, service, sms, operation_id), or None if not active.

        Notes:
            - Waits for up to 30 seconds for the number to become active.
            - Raises a TimeoutError if the wait time exceeds 30 seconds.
        """
        async with OnlineSMS(api_key=self.__api_token) as client:
            period = 30
            interval = 1
            try:
                for _ in range(period):
                    my_orders = await client.get_order_info(operation_id=operation_id)
                    if my_orders.orders[0]:
                        order = my_orders.orders[0]
                        info = {'phone': order.number, 'country': order.country, 'service': order.service,
                                'sms': order.message, 'operation_id': order.operation_id}
                        self.operation_id = order.operation_id
                        self.received_phone_number = order.number
                        return info
                    await asyncio.sleep(interval)
            except TimeoutError:
                awslogger.log_critical("Timed out waiting for active number info.")
            except Exception:
                awslogger.log_critical("Number is not active")

    async def __wait_order_info(self, operation_id: int) -> dict[str, str] | None:
        """
        Waits for SMS information associated with the specified operation ID.

        Args:
            operation_id (int): The operation ID to wait for.

        Returns:
            Optional[Dict[str, str]]: A dictionary containing SMS information
                (phone, country, service, sms, operation_id), or None if not available.

        Notes:
            - Waits for up to 60 seconds for SMS information.
        """
        async with OnlineSMS(api_key=self.__api_token) as client:
            period = 60
            interval = 5
            try:
                for _ in range(period):
                    my_orders = await client.get_order_info(operation_id=operation_id)
                    awslogger.log_info(f'waiting for sms to... {my_orders.orders[0].number}')
                    if my_orders.orders[0]:
                        order = my_orders.orders[0]
                        info = {'phone': order.number, 'country': order.country, 'service': order.service,
                                'sms': order.message, 'operation_id': order.operation_id}
                        if order.message:
                            awslogger.log_info(f'standard info: {info}')
                            return info
                    await asyncio.sleep(interval)
            except TimeoutError:
                awslogger.log_critical("Timed out waiting for SMS.")
            except Exception:
                awslogger.log_critical(f'standard info: {info}')
                return None

    async def __finish_order(self, operation_id: int) -> None:
        """
        Finishes the order associated with the specified operation ID.

        Args:
            operation_id (int): The operation ID to finish.
        """
        async with OnlineSMS(api_key=self.__api_token) as client:
            await client.finish_order(operation_id=operation_id)

    def get_balance_info(self) -> str:
        """
        Retrieves the account balance and returns it as an awaitable.

        Returns:
            str: An awaitable representing the account balance.
        """
        result = asyncio.run(self.__get_balance())
        return result

    def order_number(self) -> str | None:
        """
        Orders a new phone number or retrieves an existing active number.

        Returns:
            str: The ordered phone number.
        """
        ordered_number = asyncio.run(self.__order_number())
        awslogger.log_info(f"new active ordered_number: {ordered_number}")
        return ordered_number

    def wait_order_info(self, operation_id: int | None = None) -> dict | None:
        """
        Waits for order information related to the specified operation ID.

        Args:
            operation_id (Optional[str]): The operation ID to wait for (defaults to self.operation_id).

        Returns:
            dict | None: Information related to the order if available, else None.
        """
        operation_id = operation_id or self.operation_id
        try:
            return asyncio.run(self.__wait_order_info(operation_id))
        except ValueError:
            return None

    def finish_order(self, operation_id: int) -> None:
        """
        Finishes the order associated with the specified operation ID.

        Args:
            operation_id (int): The operation ID to finish.
        """
        asyncio.run(self.__finish_order(operation_id))
