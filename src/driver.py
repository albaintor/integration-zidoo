#!/usr/bin/env python3
"""
This module implements a Remote Two integration driver for Zidoo STB.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import logging
import os
import sys
from enum import Enum
from typing import Any, Type

import ucapi
from ucapi.media_player import States

import config
import media_player
import selector
import sensor
import setup_flow
import zidooaio
from config import ZidooEntity
from zidooaio import ZidooClient

_LOG = logging.getLogger("driver")  # avoid having __main__ in log messages
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
_LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(_LOOP)

# pylint: disable=C0103
# Global variables
api = ucapi.IntegrationAPI(_LOOP)
# Map of device_id -> Zidoo instance
_configured_devices: dict[str, ZidooClient] = {}
_remote_in_standby = False


@api.listens_to(ucapi.Events.CONNECT)
async def on_connect_cmd() -> None:
    """Connect all configured receivers when the Remote Two sends the connect command."""
    # TODO check if we were in standby and ignore the call? We'll also get an EXIT_STANDBY
    _LOG.debug("R2 connect command: connecting device(s)")
    for device in _configured_devices.values():
        # start background task
        await device.connect()
        await _LOOP.create_task(device.update())
        await api.set_device_state(ucapi.DeviceStates.CONNECTED)


@api.listens_to(ucapi.Events.DISCONNECT)
async def on_disconnect_cmd():
    """Disconnect all configured receivers when the Remote Two sends the disconnect command."""
    return
    # for device in _configured_devices.values():
    #     # start background task
    #     await device.disconnect()


@api.listens_to(ucapi.Events.ENTER_STANDBY)
async def on_enter_standby() -> None:
    """Enter standby notification from Remote Two.

    Disconnect every ZidooTV instances.
    """
    global _remote_in_standby
    _remote_in_standby = True
    _LOG.debug("Enter standby event: disconnecting device(s)")
    # for device in _configured_devices.values():
    #     # start background task
    #     await device.disconnect()


def filter_attributes(attributes, attribute_type: Type[Enum]) -> dict[str, Any]:
    """Filter attributes based on an Enum class."""
    return {k: v for k, v in attributes.items() if k in attribute_type}


@api.listens_to(ucapi.Events.EXIT_STANDBY)
async def on_exit_standby() -> None:
    """
    Exit standby notification from Remote Two.

    Connect all ZidooTV instances.
    """
    global _remote_in_standby

    _remote_in_standby = False
    _LOG.debug("Exit standby event: connecting device(s)")

    for device in _configured_devices.values():
        # start background task
        await _LOOP.create_task(device.update())


@api.listens_to(ucapi.Events.SUBSCRIBE_ENTITIES)
async def on_subscribe_entities(entity_ids: list[str]) -> None:
    """
    Subscribe to given entities.

    :param entity_ids: entity identifiers.
    """
    global _remote_in_standby

    _remote_in_standby = False
    _LOG.debug("Subscribe entities event: %s", entity_ids)
    for entity_id in entity_ids:
        entity: ZidooEntity | None = api.configured_entities.get(entity_id)
        device_id = entity.deviceid
        if device_id in _configured_devices:
            device = _configured_devices[device_id]
            if isinstance(entity, media_player.ZidooMediaPlayer):
                api.configured_entities.update_attributes(
                    entity_id, filter_attributes(device.attributes, ucapi.media_player.Attributes)
                )
            elif isinstance(entity, sensor.ZidooSensor):
                api.configured_entities.update_attributes(entity_id, entity.update_attributes())
            elif isinstance(entity, selector.ZidooSelect):
                api.configured_entities.update_attributes(entity_id, entity.update_attributes())
            continue

        device = config.devices.get(device_id)
        if device:
            _configure_new_device(device, connect=True)
        else:
            _LOG.error(
                "Failed to subscribe entity %s: no device configuration found",
                entity_id,
            )


@api.listens_to(ucapi.Events.UNSUBSCRIBE_ENTITIES)
async def on_unsubscribe_entities(entity_ids: list[str]) -> None:
    """On unsubscribe, we disconnect the objects and remove listeners for events."""
    _LOG.debug("Unsubscribe entities event: %s", entity_ids)
    devices_to_remove = set()
    for entity_id in entity_ids:
        entity: ZidooEntity | None = api.configured_entities.get(entity_id)
        device_id = entity.deviceid
        if device_id is None:
            continue
        devices_to_remove.add(device_id)

    # Keep devices that are used by other configured entities not in this list
    for entity in api.configured_entities.get_all():
        entity_id = entity.get("entity_id", None)
        if entity_id in entity_ids:
            continue
        entity: ZidooEntity | None = api.configured_entities.get(entity_id)
        device_id = entity.deviceid
        if device_id is None:
            continue
        if device_id in devices_to_remove:
            devices_to_remove.remove(device_id)

    for device_id in devices_to_remove:
        if device_id in _configured_devices:
            await _configured_devices[device_id].disconnect()
            _configured_devices[device_id].events.remove_all_listeners()


async def on_device_connected(device_id: str):
    """Handle Zidoo connection."""
    _LOG.debug("Device connected: %s", device_id)

    if device_id not in _configured_devices:
        _LOG.warning("Device %s is not configured", device_id)
        return

    # TODO #20 when multiple devices are supported, the device state logic isn't that simple anymore!
    await api.set_device_state(ucapi.DeviceStates.CONNECTED)

    for configured_entity in _get_entities(device_id):
        if configured_entity.entity_type == ucapi.EntityTypes.MEDIA_PLAYER:
            if (
                configured_entity.attributes[ucapi.media_player.Attributes.STATE]
                == ucapi.media_player.States.UNAVAILABLE
            ):
                api.configured_entities.update_attributes(
                    configured_entity.id, {ucapi.media_player.Attributes.STATE: ucapi.media_player.States.STANDBY}
                )
        elif configured_entity.entity_type == ucapi.EntityTypes.SENSOR:
            api.configured_entities.update_attributes(
                configured_entity.id, {ucapi.sensor.Attributes.STATE: ucapi.sensor.States.ON}
            )


async def on_device_disconnected(device_id: str):
    """Handle AVR disconnection."""
    _LOG.debug("AVR disconnected: %s", device_id)

    for configured_entity in _get_entities(device_id):
        if configured_entity.entity_type == ucapi.EntityTypes.MEDIA_PLAYER:
            api.configured_entities.update_attributes(
                configured_entity.id, {ucapi.media_player.Attributes.STATE: ucapi.media_player.States.UNAVAILABLE}
            )
        elif configured_entity.entity_type == ucapi.EntityTypes.SENSOR:
            api.configured_entities.update_attributes(
                configured_entity.id, {ucapi.sensor.Attributes.STATE: ucapi.sensor.States.UNAVAILABLE}
            )

    # TODO #20 when multiple devices are supported, the device state logic isn't that simple anymore!
    await api.set_device_state(ucapi.DeviceStates.DISCONNECTED)


async def on_device_connection_error(device_id: str, message):
    """Set entities of AVR to state UNAVAILABLE if AVR connection error occurred."""
    _LOG.error(message)

    for configured_entity in _get_entities(device_id):
        if configured_entity.entity_type == ucapi.EntityTypes.MEDIA_PLAYER:
            api.configured_entities.update_attributes(
                configured_entity.id, {ucapi.media_player.Attributes.STATE: ucapi.media_player.States.UNAVAILABLE}
            )

    # TODO #20 when multiple devices are supported, the device state logic isn't that simple anymore!
    await api.set_device_state(ucapi.DeviceStates.ERROR)


async def handle_device_address_change(device_id: str, address: str) -> None:
    """Update device configuration with changed IP address."""
    device = config.devices.get(device_id)
    if device and device.address != address:
        _LOG.info(
            "Updating IP address of configured device %s: %s -> %s",
            device_id,
            device.address,
            address,
        )
        device.address = address
        config.devices.update(device)


async def on_device_update(device_id: str, update: dict[str, Any] | None) -> None:
    """
    Update attributes of configured media-player entity if device properties changed.

    :param device_id: AVR identifier
    :param update: dictionary containing the updated properties or None if
    """
    if update is None:
        if device_id not in _configured_devices:
            return
        device = _configured_devices[device_id]
        update = device.attributes
    else:
        _LOG.info("[%s] Zidoo update: %s", device_id, update)

    attributes = None

    # TODO awkward logic: this needs better support from the integration library
    for configured_entity in _get_entities(device_id):
        if isinstance(configured_entity, media_player.ZidooMediaPlayer):
            attributes = filter_attributes(update, ucapi.media_player.Attributes)
        elif isinstance(configured_entity, sensor.ZidooSensor):
            attributes = configured_entity.update_attributes(update)
        elif isinstance(configured_entity, selector.ZidooSelect):
            attributes = configured_entity.update_attributes(update)

        if attributes:
            api.configured_entities.update_attributes(configured_entity.id, attributes)


def _get_entities(device_id: str, include_all=False) -> list[ZidooEntity]:
    """
    Return all associated entities of the given device.

    :param device_id: the device identifier
    :param include_all: include both configured and available entities
    :return: list of entities
    """
    entities = []
    for entity_entry in api.configured_entities.get_all():
        entity: ZidooEntity | None = api.configured_entities.get(entity_entry.get("entity_id", ""))
        if entity is None or entity.deviceid != device_id:
            continue
        entities.append(entity)
    if not include_all:
        return entities
    for entity_entry in api.available_entities.get_all():
        entity: ZidooEntity | None = api.available_entities.get(entity_entry.get("entity_id", ""))
        if entity is None or entity.deviceid != device_id:
            continue
        entities.append(entity)
    return entities


def _configure_new_device(device_config: config.ConfigDevice, connect: bool = True) -> None:
    """
    Create and configure a new device.

    Supported entities of the device are created and registered in the integration library as available entities.

    :param device_config: the device configuration.
    :param connect: True: start connection to receiver.
    """
    # the device should not yet be configured, but better be safe
    if device_config.id in _configured_devices:
        _LOG.debug("Existing config device updated, update the running device %s", device_config)
        device = _configured_devices[device_config.id]
        asyncio.create_task(device.disconnect())
        device.update_config(device_config)
    else:
        device = ZidooClient(device_config)
        # device.events.on(zidooaio.Events.CONNECTED, on_device_connected)
        device.events.on(zidooaio.Events.ERROR, on_device_connection_error)
        device.events.on(zidooaio.Events.UPDATE, on_device_update)
        # receiver.events.on(avr.Events.IP_ADDRESS_CHANGED, handle_avr_address_change)
        _configured_devices[device_config.id] = device

    if connect:
        # start background connection task
        _LOOP.create_task(device.update())
        _LOOP.create_task(on_device_connected(device_config.id))
    _register_available_entities(device_config, device)


def _register_available_entities(config_device: config.ConfigDevice, device: ZidooClient) -> None:
    """
    Create entities for given receiver device and register them as available entities.

    :param config_device: device
    """
    entities = [
        media_player.ZidooMediaPlayer(config_device, device),
        selector.ZidooAudioStreamSelect(config_device, device),
        selector.ZidooSubtitleStreamSelect(config_device, device),
        sensor.ZidooAudioStream(config_device, device),
        sensor.ZidooSubtitleStream(config_device, device),
    ]
    for entity in entities:
        if api.available_entities.contains(entity.id):
            api.available_entities.remove(entity.id)
        api.available_entities.add(entity)


def on_device_added(device: config.ConfigDevice) -> None:
    """Handle a newly added device in the configuration."""
    _LOG.debug("New device added: %s", device)
    _configure_new_device(device, connect=False)


def on_device_updated(device: config.ConfigDevice) -> None:
    """Handle an updated device in the configuration."""
    _LOG.debug("Device config updated: %s, reconnect with new configuration", device)
    if device.id in _configured_devices:
        _LOG.debug("Disconnecting from removed device %s", device.id)
        configured = _configured_devices.pop(device.id)
        configured.events.remove_all_listeners()
        for entity in _get_entities(configured.id):
            api.configured_entities.remove(entity.id)
            api.available_entities.remove(entity.id)
    _configure_new_device(device, connect=True)


def on_device_removed(device: config.ConfigDevice | None) -> None:
    """Handle a removed device in the configuration."""
    if device is None:
        _LOG.debug("Configuration cleared, disconnecting & removing all configured AVR instances")
        for configured in _configured_devices.values():
            _LOOP.create_task(_async_remove(configured))
        _configured_devices.clear()
        api.configured_entities.clear()
        api.available_entities.clear()
    else:
        if device.id in _configured_devices:
            _LOG.debug("Disconnecting from removed device %s", device.id)
            configured = _configured_devices.pop(device.id)
            _LOOP.create_task(_async_remove(configured))
            for entity in _get_entities(configured.id):
                api.configured_entities.remove(entity.id)
                api.available_entities.remove(entity.id)


async def _async_remove(device: ZidooClient) -> None:
    """Disconnect from receiver and remove all listeners."""
    # await device.disconnect()
    device.events.remove_all_listeners()


async def main():
    """Start the Remote Two integration driver."""
    logging.basicConfig()

    level = os.getenv("UC_LOG_LEVEL", "DEBUG").upper()
    logging.getLogger("zidooaio").setLevel(level)
    logging.getLogger("discover").setLevel(level)
    logging.getLogger("driver").setLevel(level)
    logging.getLogger("media_player").setLevel(level)
    logging.getLogger("setup_flow").setLevel(level)
    # logging.getLogger("remote").setLevel(level)
    logging.getLogger("sensor").setLevel(level)
    logging.getLogger("selector").setLevel(level)

    config.devices = config.Devices(api.config_dir_path, on_device_added, on_device_removed, on_device_updated)
    for device in config.devices.all():
        _LOG.debug("UC Zidoo device %s %s", device.id, device.address)
        _configure_new_device(device, connect=False)

    # _LOOP.create_task(receiver_status_poller())
    for device in _configured_devices.values():
        if device.state in [States.OFF, States.UNKNOWN]:
            continue
        _LOOP.create_task(device.update())

    await api.init("driver.json", setup_flow.driver_setup_handler)


if __name__ == "__main__":
    _LOOP.run_until_complete(main())
    _LOOP.run_forever()
