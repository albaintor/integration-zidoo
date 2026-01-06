"""
Test connection script for Kodi integration driver.

:copyright: (c) 2025 by Unfolded Circle ApS.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

# pylint: disable=all
# flake8: noqa

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Any

from rich import print_json

import zidooaio
from config import DeviceInstance
from zidooaio import ZidooRC

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
_LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(_LOOP)

address = "192.168.1.23"
client: ZidooRC | None = None


async def on_device_update(device_id: str, update: dict[str, Any] | None) -> None:
    print_json(data=update)


async def cleaning():
    if client:
        await client.disconnect()
    exit(0)


def signal_handler(sig, frame):
    asyncio.create_task(cleaning())


async def main():
    global client
    _LOG.debug("Start connection")
    # await pair()
    # exit(0)
    client = ZidooRC(
        device_config=DeviceInstance(
            id="zidoo",
            name="Zidoo",
            address=address,
        ),
    )
    # await client.power_on()
    client.events.on(zidooaio.Events.UPDATE, on_device_update)
    await client.connect()

    await asyncio.sleep(2)
    properties = await client.get_system_info()
    print("Properties :")
    print_json(data=properties)
    properties = await client.get_playing_info()
    print("Info :")
    if properties.get("date", None) and isinstance(properties["date"], datetime):
        properties["date"] = str(properties["date"])
    print_json(data=properties)
    properties = {
        "title": client.media_title,
        "artist": client.media_artist,
        "album": client.media_album_name,
        "media image": client.media_image_url,
        "status": client.state,
    }
    print("Media info :")
    print_json(data=properties)
    # _LOOP.create_task(client.update())
    while True:
        await asyncio.sleep(10)


if __name__ == "__main__":
    _LOG = logging.getLogger(__name__)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logging.basicConfig(handlers=[ch])
    logging.getLogger("zidooaio").setLevel(logging.DEBUG)
    logging.getLogger("media_player").setLevel(logging.DEBUG)
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    signal.signal(signal.SIGINT, signal_handler)
    _LOOP.run_until_complete(main())
    _LOOP.run_forever()
