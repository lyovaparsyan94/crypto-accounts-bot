import asyncio

from configs.constants import ONLINE_COUNTRY_CODE, ONLINE_SIM_SERVICE, SIM_API_TOKEN
from dotenv import load_dotenv
from pyonlinesim import OnlineSMS


class AsyncOnlimeSimHandler:
    load_dotenv()

    def __init__(self):
        self.__api_token = SIM_API_TOKEN
        self.operation_id = None
        self.received_phone_number = None
        self.can_receive = True

    async def get_balance(self) -> str:
        async with OnlineSMS(api_key=self.__api_token) as client:
            result = await client.get_balance()
            return result

    async def get_service_info(self) -> dict:
        async with OnlineSMS(api_key=self.__api_token) as client:
            countryes = await client.get_services(country=ONLINE_COUNTRY_CODE)
            for service in countryes.services:
                if service.service == ONLINE_SIM_SERVICE:
                    print(
                        f'ID: {service.id} | Available Numbers: {service.count} | Service: {service.service} | Price: {service.price}')
                    return {f"{ONLINE_SIM_SERVICE}": service.id, 'available_numbers': service.count,
                            'service_name': ONLINE_SIM_SERVICE}

    async def receive_number(self):
        received_number = self.order_number()
        if received_number:
            print(f'received_number is : {received_number}')

    async def __order_number(self, service: str = ONLINE_SIM_SERVICE, country: int = ONLINE_COUNTRY_CODE) -> str:
        async with OnlineSMS(api_key=self.__api_token) as client:
            order = await client.order_number(service=service, country=country, number=True)
            if order:
                received_number = order.number
                self.operation_id = order.operation_id
                self.received_phone_number = received_number
                self.can_receive = False
                return received_number

    async def __wait_order_info(self, operation_id: int):
        async with OnlineSMS(api_key=self.__api_token) as client:
            try:
                for _ in range(5):
                    my_orders = await client.get_order_info(operation_id=operation_id)
                    if my_orders.orders:
                        order = my_orders.orders[0]
                        if order.message:
                            info = {'phone': order.number, 'country': order.country, 'service': order.service,
                                    'sms': order.message, 'operation_id': order.operation_id}
                            print(order.number)
                            return info
                    await asyncio.sleep(60)  # Wait for 1 minute
            except TimeoutError:
                print("Timed out waiting for SMS.")
            finally:
                return None  # Return None if no SMS received within the timeout

    async def __finish_order(self, operation_id: int = None) -> None:
        async with OnlineSMS(api_key=self.__api_token) as client:
            await client.finish_order(operation_id=operation_id)

    def get_balance_info(self):
        result = asyncio.run(self.get_balance())
        return result

    def order_number(self):
        ordered_number = asyncio.run(self.__order_number())
        print(f"ordered_number: {ordered_number}")
        return ordered_number

    def wait_order_info(self):
        info = asyncio.run(self.__wait_order_info(self.operation_id))
        print(f'waited for order_info: {info}')
        return info

    def finish_order(self, operation_id):
        asyncio.run(self.__finish_order(operation_id))


# simhandler = AsyncOnlimeSimHandler()
# simhandler.wait_order_info()
# simhandler.order_number()
# asyncio.run(simhandler.get_service_info())
