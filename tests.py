import asyncio
from pathlib import Path

from pyrogram import Client

from tgintegration import BotController
from tgintegration import Response

from datetime import date


examples_dir = Path(__file__).parent.parent.absolute()
SESSION_NAME: str = "tgintegration_examples"


def create_client(session_name: str = SESSION_NAME) -> Client:
    # client = Client(
    #     session_name=session_name,
    #     workdir=examples_dir,
    #     config_file="config.ini",
    # )
    client = Client(
        "my_account",
        api_id=2137055,
        api_hash="be89395c5ac5688dbbca82886b6e4dec"
    )
    # client.load_config()
    return client


async def run_example(client: Client):
    controller = BotController(
        peer="@StatInfoTestBot",
        client=client,
        max_wait=8,  # Maximum timeout for responses (optional)
        wait_consecutive=2,  # Minimum time to wait for more/consecutive messages (optional)
        raise_no_response=True,  # Raise `InvalidResponseError` when no response received (defaults to True)
        global_action_delay=2.5,  # Choosing a rather high delay so we can follow along in realtime (optional)
    )

    # expecting 2 messages in reply for /start command
    async with controller.collect(count=2) as response:  # type: Response
        await controller.send_command("start")

    assert response.num_messages == 2


    async with controller.collect(count=1) as response:  # type: Response
        await controller.send_command("help")

    assert response.num_messages == 1
    assert "The following commands are available" in response.full_text


    async with controller.collect(count=1) as response:  # type: Response
        await controller.send_command("statistics")

    assert response.num_messages == 1

    # expecting to get statistics for today
    current_date = str(date.today())
    assert current_date in response.full_text


    async with controller.collect(count=1) as response:  # type: Response
        await controller.send_command("country")

    assert response.num_messages == 1
    assert "Please, enter country name." in response.full_text


    async with controller.collect(count=1) as response:  # type: Response
        await client.send_message(controller.peer_id, "Russian Federation")

    assert response.num_messages == 1
    assert "Russian Federation" in response.full_text


    async with controller.collect(count=1) as response:  # type: Response
        await controller.send_command("contacts")

    assert response.num_messages == 1
    assert "4 members" in response.full_text


    async with controller.collect(count=1) as response:  # type: Response
        await client.send_message(controller.peer_id, "hi")

    assert response.num_messages == 1
    assert "To get to know me better" in response.full_text


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_example(create_client()))
