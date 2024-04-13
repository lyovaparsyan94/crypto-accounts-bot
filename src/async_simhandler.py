import asyncio

from config import configs
from logs.aws_logger import awslogger
from pyonlinesim import OnlineSMS
from repository.file_repository import UserSimDataRepository


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
        self.repo = UserSimDataRepository()

    async def get_balance_info(self) -> str:
        """
        Retrieves the account balance from the SMS service.

        Returns:
            str: The account balance as a string.
        """
        async with OnlineSMS(api_key=self.__api_token) as client:
            result = await client.get_balance()
            awslogger.log_info(f'balance: {result.balance}, frozen: {result.frozen_balance}')
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
                            'service_name': configs.aws_configs.ONLINE_SIM_SERVICE, }

    async def order_phone_number(self, service: str = configs.aws_configs.ONLINE_SIM_SERVICE,
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
                self.repo.save_sim_data(current_sim)
                awslogger.log_info(f"new active ordered number: {received_number}")
                return received_number

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
                                'sms': order.message, 'operation_id': order.operation_id, }
                        self.operation_id = order.operation_id
                        self.received_phone_number = order.number
                        return info
                    await asyncio.sleep(interval)
            except TimeoutError:
                awslogger.log_critical("Timed out waiting for active number info.")
            except Exception:
                awslogger.log_critical("Number is not active")

    async def wait_order_info(self, operation_id: int | None = None) -> dict | None:
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
            operation_id = operation_id or self.operation_id
            period = 60
            interval = 5
            try:
                for _ in range(period):
                    my_orders = await client.get_order_info(operation_id=operation_id)
                    awslogger.log_info(f'waiting for sms to... {my_orders.orders[0].number}')
                    if my_orders.orders[0]:
                        order = my_orders.orders[0]
                        info = {'phone': order.number, 'country': order.country, 'service': order.service,
                                'sms': order.message, 'operation_id': order.operation_id, }
                        if order.message:
                            awslogger.log_info(f'standard info: {info}')
                            return info
                    await asyncio.sleep(interval)
            except TimeoutError:
                awslogger.log_critical("Timed out waiting for SMS.")
            except Exception:
                awslogger.log_critical(f'received info: {info}')
                return None

    async def close_card(self, operation_id: int) -> None:
        """
        Finishes the order associated with the specified operation ID.

        Args:
            operation_id (int): The operation ID to finish.
        """
        async with OnlineSMS(api_key=self.__api_token) as client:
            await client.finish_order(operation_id=operation_id)
