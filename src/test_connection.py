"""
Test connection script for Kodi integration driver.

:copyright: (c) 2025 by Unfolded Circle ApS.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import logging
import sys
from typing import Any

from rich import print_json, print
from config import DeviceInstance
from zidooaio import ZidooRC, Events

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
_LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(_LOOP)

address = "192.168.1.23"

async def on_device_update(device_id: str, update: dict[str, Any] | None) -> None:
    print_json(data=update)


async def main():
    _LOG.debug("Start connection")
    # await pair()
    # exit(0)
    client = ZidooRC(
        device_config=DeviceInstance(
            id="zidoo",
            name="Zidoo",
            address=address,
            net_mac_address="80:0a:80:55:e0:09",
            wifi_mac_address="",
            always_on=False
        )
    )
    # await client.power_on()
    client.events.on(Events.UPDATE, on_device_update)
    data = await client.connect()
    print("Connection info :")
    print_json(data=data)
    await _LOOP.create_task(client.update())
    await asyncio.sleep(2)
    properties = client._media_info
    print("Properties :")
    print(properties)
    # await client.play_pause()
    # await asyncio.sleep(4)
    # await client.play_pause()

if __name__ == "__main__":
    _LOG = logging.getLogger(__name__)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logging.basicConfig(handlers=[ch])
    logging.getLogger("client").setLevel(logging.DEBUG)
    logging.getLogger("zidooaio").setLevel(logging.DEBUG)
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    _LOOP.run_until_complete(main())
    _LOOP.run_forever()
