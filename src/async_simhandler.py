import asyncio
import os
import time

from dotenv import load_dotenv
from pyonlinesim import OnlineSMS

from configs.constants import ONLINE_SIM_SERVICE, ONLINE_COUNTRY_CODE


class AsyncOnlimeSimHandler:
    load_dotenv()

    def __init__(self):
        self.__api_token = os.getenv('SIM_API_TOKEN')
        self.received_phone_number = None
        self.can_receive = True

    async def get_balance(self) -> str:
        async with OnlineSMS(api_key=self.__api_token) as client:
            result = await client.get_balance()  # Balance(response='1', balance=0.0, frozen_balance=0.0)
            print(result)
            return result

    async def get_service_info(self, country: str = ONLINE_COUNTRY_CODE,
                               service_name: str = ONLINE_SIM_SERVICE) -> dict:
        async with OnlineSMS(api_key=self.__api_token) as client:
            country = await client.get_services(country=country)
            counter = 1
            for service in country.services:
                counter += 1
                if service.service == service_name:
                    print(
                        f'ID: {service.id} | Available Numbers: {service.count} | Service: {service.service} | Price: {service.price}')
                    return {f"{ONLINE_SIM_SERVICE}": service.id, 'available_numbers': service.count,
                            'service_name': ONLINE_SIM_SERVICE}

    async def receive_number(self):
        received_number = await self.__order_number()
        print(f'waiting for number: {received_number}')
        if received_number:
            print(f'now received_number is : {received_number}')
            self.can_receive = False
            self.received_phone_number = received_number

    async def __order_number(self, service: str = ONLINE_SIM_SERVICE, country: int = ONLINE_COUNTRY_CODE) -> str:
        async with OnlineSMS(api_key=self.__api_token) as client:
            if self.can_receive:
                order = await client.order_number(service=service, country=country, number=True)
                print(f'Operation ID: {order.operation_id} | Received number: {order.number}')
                received_number = order.number
                return received_number
            else:
                raise ValueError('Impossible to receive new number')

    async def get_order_info(self, operation_id: int = None) -> None:
        async with OnlineSMS(api_key=self.__api_token) as client:
            my_orders = await client.get_order_info(operation_id=operation_id)  # Get Orders
            order = my_orders.orders[0]  # Get First Order
            print('working')
            if order.message:
                return my_orders

    async def get_order_info_with_timeout(self, operation_id=None):
        async with OnlineSMS(api_key=self.__api_token) as client:
            try:
                if self.received_phone_number:
                    for _ in range(5):
                        my_orders = await client.get_order_info(operation_id=operation_id)
                        if my_orders.orders:
                            order = my_orders.orders[0]
                            info = {'phone': order.number, 'country': order.country, 'service': order.service,
                                    'sms': order.message, 'operation_id': order.operation_id}
                            print(order.number)
                            return info  # Return the SMS code if received
                        await asyncio.sleep(60)  # Wait for 1 minute
                else:
                    raise ValueError
            except asyncio.TimeoutError:
                print("Timed out waiting for SMS.")
            except ValueError:
                print('cannot get order info')
            finally:
                await self.finish_order(37)
                return None  # Return None if no SMS received within the timeout

    async def finish_order(self, operation_id: int = None) -> None:
        async with OnlineSMS(api_key=self.__api_token) as client:
            response = await client.finish_order(operation_id=operation_id)
            print(response)  # OrderManaged(response='1', operation_id=551166)


simhandler = AsyncOnlimeSimHandler()
# asyncio.run(simhandler.receive_number())
asyncio.run(simhandler.get_service_info())
asyncio.run(simhandler.get_order_info_with_timeout())
