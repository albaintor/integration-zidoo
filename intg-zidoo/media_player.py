"""
Media-player entity functions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from typing import Any

import zidooaio
from config import DeviceInstance, create_entity_id
from ucapi import EntityTypes, MediaPlayer, StatusCodes
from ucapi.media_player import Attributes, Commands, DeviceClasses, Features, States, MediaType

from zidooaio import ZidooRC, ZKEYS

_LOG = logging.getLogger(__name__)

# Mapping of a device state to a media-player entity state
MEDIA_PLAYER_STATE_MAPPING = {
    zidooaio.States.ON: States.ON,
    zidooaio.States.OFF: States.OFF,
    zidooaio.States.PAUSED: States.PAUSED,
    zidooaio.States.PLAYING: States.PLAYING,
    zidooaio.States.UNAVAILABLE: States.UNAVAILABLE,
    zidooaio.States.UNKNOWN: States.UNKNOWN,
}


class ZidooMediaPlayer(MediaPlayer):
    """Representation of a Sony Media Player entity."""

    def __init__(self, config_device: DeviceInstance, device: ZidooRC):
        """Initialize the class."""
        self._device = device

        entity_id = create_entity_id(config_device.id, EntityTypes.MEDIA_PLAYER)
        features = [
            Features.ON_OFF,
            Features.TOGGLE,
            Features.VOLUME_UP_DOWN,
            Features.MUTE_TOGGLE,
            Features.SELECT_SOURCE,
            Features.MEDIA_TITLE,
            Features.MEDIA_IMAGE_URL,
            Features.MEDIA_TYPE,
            Features.PLAY_PAUSE,
            Features.MEDIA_POSITION,
            Features.MEDIA_DURATION,
            Features.DPAD,
            Features.SETTINGS,
            Features.STOP,
            Features.FAST_FORWARD,
            Features.REWIND,
            Features.RECORD,
            Features.MENU,
            Features.NUMPAD,
            Features.CHANNEL_SWITCHER,
            Features.NEXT,
            Features.PREVIOUS,
            Features.CONTEXT_MENU,
            Features.INFO,
            Features.AUDIO_TRACK,
            Features.SUBTITLE,
        ]
        attributes = {
            Attributes.STATE: States.UNAVAILABLE,
            Attributes.SOURCE: "",
            Attributes.SOURCE_LIST: [],
            Attributes.MEDIA_IMAGE_URL: "",
            Attributes.MEDIA_TITLE: "",
            Attributes.MEDIA_POSITION: 0,
            Attributes.MEDIA_DURATION: 0,
            Attributes.MEDIA_TYPE: MediaType.VIDEO,
        }
        # # use sound mode support & name from configuration: receiver might not yet be connected
        # if device.support_sound_mode:
        #     features.append(Features.SELECT_SOUND_MODE)
        #     attributes[Attributes.SOUND_MODE] = ""
        #     attributes[Attributes.SOUND_MODE_LIST] = []

        super().__init__(
            entity_id,
            config_device.name,
            features,
            attributes,
            device_class=DeviceClasses.SET_TOP_BOX,
        )

    async def command(self, cmd_id: str, params: dict[str, Any] | None = None) -> StatusCodes:
        """
        Media-player entity command handler.

        Called by the integration-API if a command is sent to a configured media-player entity.

        :param cmd_id: command
        :param params: optional command parameters
        :return: status code of the command request
        """
        _LOG.info("Got %s command request: %s %s", self.id, cmd_id, params)

        if self._device is None:
            _LOG.warning("No device instance for entity: %s", self.id)
            return StatusCodes.SERVICE_UNAVAILABLE

        if cmd_id == Commands.VOLUME_UP:
            res = await self._device.volume_up()
        elif cmd_id == Commands.VOLUME_DOWN:
            res = await self._device.volume_down()
        elif cmd_id == Commands.MUTE_TOGGLE:
            res = await self._device.mute_volume()
        elif cmd_id == Commands.ON:
            await self._device.turn_on()
            return StatusCodes.OK
        elif cmd_id == Commands.OFF:
            res = await self._device.turn_off()
        elif cmd_id == Commands.TOGGLE:
            res = await self._device.async_power_toggle()
        elif cmd_id == Commands.SELECT_SOURCE:
            res = await self._device.start_app(params.get("source"))
        elif cmd_id == Commands.NEXT:
            res = await self._device.media_next_track()
        elif cmd_id == Commands.PREVIOUS:
            res = await self._device.media_previous_track()
        elif cmd_id == Commands.CHANNEL_UP:
            res = await self._device._send_key(ZKEYS.ZKEY_PAGE_UP)
        elif cmd_id == Commands.CHANNEL_DOWN:
            res = await self._device._send_key(ZKEYS.ZKEY_PAGE_DOWN)
        elif cmd_id == Commands.PLAY_PAUSE:
            res = await self._device.media_play_pause()
        elif cmd_id == Commands.STOP:
            res = await self._device.media_stop()
        elif cmd_id == Commands.FAST_FORWARD:
            res = await self._device._send_key(ZKEYS.ZKEY_MEDIA_FORWARDS)
        elif cmd_id == Commands.REWIND:
            res = await self._device._send_key(ZKEYS.ZKEY_MEDIA_BACKWARDS)
        elif cmd_id == Commands.RECORD:
            res = await self._device._send_key(ZKEYS.ZKEY_RECORD)
        elif cmd_id == Commands.CURSOR_UP:
            res = await self._device._send_key(ZKEYS.ZKEY_UP)
        elif cmd_id == Commands.CURSOR_DOWN:
            res = await self._device._send_key(ZKEYS.ZKEY_DOWN)
        elif cmd_id == Commands.CURSOR_LEFT:
            res = await self._device._send_key(ZKEYS.ZKEY_LEFT)
        elif cmd_id == Commands.CURSOR_RIGHT:
            res = await self._device._send_key(ZKEYS.ZKEY_RIGHT)
        elif cmd_id == Commands.CURSOR_ENTER:
            res = await self._device._send_key(ZKEYS.ZKEY_OK)
        elif cmd_id == Commands.BACK:
            res = await self._device._send_key(ZKEYS.ZKEY_BACK)
        elif cmd_id == Commands.MENU:
            res = await self._device._send_key(ZKEYS.ZKEY_MENU)
        elif cmd_id == Commands.HOME:
            res = await self._device._send_key(ZKEYS.ZKEY_HOME)
        elif cmd_id == Commands.SETTINGS:
            res = await self._device._send_key(ZKEYS.ZKEY_APP_SWITCH)
        elif cmd_id == Commands.CONTEXT_MENU:
            res = await self._device._send_key(ZKEYS.ZKEY_POPUP_MENU)
        elif cmd_id == Commands.INFO:
            res = await self._device._send_key(ZKEYS.ZKEY_INFO)
        elif cmd_id == Commands.AUDIO_TRACK:
            res = await self._device._send_key(ZKEYS.ZKEY_AUDIO)
        elif cmd_id == Commands.SUBTITLE:
            res = await self._device._send_key(ZKEYS.ZKEY_SUBTITLE)
        elif cmd_id == Commands.DIGIT_0:
            res = await self._device._send_key(ZKEYS.ZKEY_NUM_0)
        elif cmd_id == Commands.DIGIT_1:
            res = await self._device._send_key(ZKEYS.ZKEY_NUM_1)
        elif cmd_id == Commands.DIGIT_2:
            res = await self._device._send_key(ZKEYS.ZKEY_NUM_2)
        elif cmd_id == Commands.DIGIT_3:
            res = await self._device._send_key(ZKEYS.ZKEY_NUM_3)
        elif cmd_id == Commands.DIGIT_4:
            res = await self._device._send_key(ZKEYS.ZKEY_NUM_4)
        elif cmd_id == Commands.DIGIT_5:
            res = await self._device._send_key(ZKEYS.ZKEY_NUM_5)
        elif cmd_id == Commands.DIGIT_6:
            res = await self._device._send_key(ZKEYS.ZKEY_NUM_6)
        elif cmd_id == Commands.DIGIT_7:
            res = await self._device._send_key(ZKEYS.ZKEY_NUM_7)
        elif cmd_id == Commands.DIGIT_8:
            res = await self._device._send_key(ZKEYS.ZKEY_NUM_8)
        elif cmd_id == Commands.DIGIT_9:
            res = await self._device._send_key(ZKEYS.ZKEY_NUM_9)
        else:
            return StatusCodes.NOT_IMPLEMENTED

        if res:
            return StatusCodes.OK
        return StatusCodes.BAD_REQUEST

    def filter_changed_attributes(self, update: dict[str, Any]) -> dict[str, Any]:
        """
        Filter the given attributes and return only the changed values.

        :param update: dictionary with attributes.
        :return: filtered entity attributes containing changed attributes only.
        """
        attributes = {}

        if len(self.attributes[Attributes.SOURCE_LIST]) == 0:
            update[Attributes.SOURCE_LIST] = self._device.source_list

        if Attributes.STATE in update:
            state = state_from_device(update[Attributes.STATE])
            attributes = self._key_update_helper(Attributes.STATE, state, attributes)

        for attr in [
            Attributes.SOURCE,
            Attributes.SOURCE_LIST,
            Attributes.MEDIA_IMAGE_URL,
            Attributes.MEDIA_TITLE,
            Attributes.MEDIA_POSITION,
            Attributes.MEDIA_DURATION,
            Attributes.MEDIA_TYPE,
            Attributes.MEDIA_ALBUM,
            Attributes.MEDIA_ARTIST,
        ]:
            if attr in update:
                attributes = self._key_update_helper(attr, update[attr], attributes)

        if Attributes.STATE in attributes:
            if attributes[Attributes.STATE] == States.OFF:
                attributes[Attributes.MEDIA_IMAGE_URL] = ""
                attributes[Attributes.MEDIA_TITLE] = ""
                attributes[Attributes.MEDIA_TYPE] = ""
                attributes[Attributes.SOURCE] = ""
                attributes[Attributes.MEDIA_ALBUM] = ""
                attributes[Attributes.MEDIA_ARTIST] = ""
                attributes[Attributes.MEDIA_POSITION] = 0
                attributes[Attributes.MEDIA_DURATION] = 0

        return attributes

    def _key_update_helper(self, key: str, value: str | None, attributes):
        if value is None:
            return attributes

        if key in self.attributes:
            if self.attributes[key] != value:
                attributes[key] = value
        else:
            attributes[key] = value

        return attributes


def state_from_device(client_state: zidooaio.States) -> States:
    """
    Convert Device state to UC API media-player state.

    :param client_state: Orange STB  state
    :return: UC API media_player state
    """
    if client_state in MEDIA_PLAYER_STATE_MAPPING:
        return MEDIA_PLAYER_STATE_MAPPING[client_state]
    return States.UNKNOWN
