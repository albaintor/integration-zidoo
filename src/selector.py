"""
Select entity functions.

:copyright: (c) 2026 by Albaintor
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from enum import Enum
from typing import Any

from ucapi import StatusCodes, Select, EntityTypes
from ucapi.api_definitions import CommandHandler

import zidooaio
from config import ConfigDevice, ZidooEntity, create_entity_id
from const import ZidooSelects


class States(str, Enum):
    """Select entity states."""

    ON = "ON"


_LOG = logging.getLogger(__name__)


# pylint: disable=W1405,R0801
class ZidooSelect(ZidooEntity, Select):
    """Representation of a Zidoo select entity."""

    ENTITY_NAME = "select"
    SELECT_NAME: ZidooSelects

    # pylint: disable=R0917
    def __init__(
        self,
        entity_id: str,
        name: str | dict[str, str],
        config_device: ConfigDevice,
        device: zidooaio.ZidooClient,
        select_handler: CommandHandler,
    ):
        """Initialize the class."""
        # pylint: disable = R0801
        features = []
        attributes = dict[Any, Any]()
        self._config_device = config_device
        self._device: zidooaio.ZidooClient = device
        self._state: States = States.ON
        self._select_handler: CommandHandler = select_handler
        super().__init__(identifier=entity_id, name=name, attributes=attributes)

    @property
    def deviceid(self) -> str:
        """Return device identifier."""
        return self._device.id

    @property
    def current_option(self) -> str:
        """Return select value."""
        raise NotImplementedError()

    @property
    def select_options(self) -> list[str]:
        """Return selection list."""
        raise NotImplementedError()

    def update_attributes(self, update: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Return updated selector value from full update if provided or sensor value if no udpate is provided."""
        if update:
            if self.SELECT_NAME in update:
                return update[self.SELECT_NAME]
            return None
        return {
            "current_option": self.current_option,
            "options": self.select_options,
        }

    async def command(self, cmd_id: str, params: dict[str, Any] | None = None, *, websocket: Any) -> StatusCodes:
        """Process selector command."""
        # pylint: disable=R0911
        if cmd_id == "select_option" and params:
            option = params.get("option", None)
            return await self._select_handler(option)
        options = self.select_options
        if cmd_id == "select_first" and len(options) > 0:
            return await self._select_handler(options[0])
        if cmd_id == "select_last" and len(options) > 0:
            return await self._select_handler(options[len(options) - 1])
        if cmd_id == "select_next" and len(options) > 0:
            cycle = params.get("cycle", False)
            try:
                index = options.index(self.current_option) + 1
                if not cycle and index >= len(options):
                    return StatusCodes.OK
                if index >= len(options):
                    index = 0
                return await self._select_handler(options[index])
            except ValueError as ex:
                _LOG.warning(
                    "[%s] Invalid option %s in list %s %s",
                    self._config_device.address,
                    self.current_option,
                    options,
                    ex,
                )
                return StatusCodes.BAD_REQUEST
        if cmd_id == "select_previous" and len(options) > 0:
            cycle = params.get("cycle", False)
            try:
                index = options.index(self.current_option) - 1
                if not cycle and index < 0:
                    return StatusCodes.OK
                if index < 0:
                    index = len(options) - 1
                return await self._select_handler(options[index])
            except ValueError as ex:
                _LOG.warning(
                    "[%s] Invalid option %s in list %s %s",
                    self._config_device.address,
                    self.current_option,
                    options,
                    ex,
                )
                return StatusCodes.BAD_REQUEST
        return StatusCodes.BAD_REQUEST


class ZidooAudioStreamSelect(ZidooSelect):
    """Current audio stream selector entity."""

    ENTITY_NAME = "audio_stream"
    SELECT_NAME = ZidooSelects.SELECT_AUDIO_STREAM

    def __init__(self, config_device: ConfigDevice, device: zidooaio.ZidooClient):
        """Initialize the class."""
        # pylint: disable=W1405,R0801
        entity_id = f"{create_entity_id(config_device.id, EntityTypes.SELECT)}.{self.ENTITY_NAME}"
        super().__init__(
            entity_id,
            {
                "en": f"{config_device.get_device_part()}Audio stream",
                "fr": f"{config_device.get_device_part()}Piste audio",
            },
            config_device,
            device,
            device.select_audio_track,
        )

    @property
    def current_option(self) -> str:
        """Return selector value."""
        return self._device.audio_track

    @property
    def select_options(self) -> list[str]:
        """Return selection list."""
        return self._device.audio_tracks


class ZidooSubtitleStreamSelect(ZidooSelect):
    """Current subtitle stream selector entity."""

    ENTITY_NAME = "subtitle_stream"
    SELECT_NAME = ZidooSelects.SELECT_SUBTITLE_STREAM

    def __init__(self, config_device: ConfigDevice, device: zidooaio.ZidooClient):
        """Initialize the class."""
        # pylint: disable=W1405
        entity_id = f"{create_entity_id(config_device.id, EntityTypes.SELECT)}.{self.ENTITY_NAME}"
        super().__init__(
            entity_id,
            {
                "en": f"{config_device.get_device_part()}Subtitle stream",
                "fr": f"{config_device.get_device_part()}Piste sous-titres",
            },
            config_device,
            device,
            device.select_subtitle_track,
        )

    @property
    def current_option(self) -> str:
        """Return selector value."""
        return self._device.subtitle_track

    @property
    def select_options(self) -> list[str]:
        """Return selection list."""
        return self._device.subtitle_tracks


# class KodiChapterSelect(ZidooSelect):
#     """Chapter selector entity."""
#
#     ENTITY_NAME = "chapter"
#     SELECT_NAME = ZidooSelects.SELECT_CHAPTER
#
#     def __init__(self, config_device: ConfigDevice, device: zidooaio.ZidooClient):
#         """Initialize the class."""
#         entity_id = f"{create_entity_id(config_device.id, EntityTypes.SELECT)}.{self.ENTITY_NAME}"
#         super().__init__(
#             entity_id,
#             {
#                 "en": f"{config_device.get_device_part()}Chapter",
#                 "fr": f"{config_device.get_device_part()}Chapitre",
#             },
#             config_device,
#             device,
#             device.select_chapter,
#         )
#
#     @property
#     def current_option(self) -> str:
#         """Return selector value."""
#         return self._device.current_chapter if self._device.current_chapter is not None else ""
#
#     @property
#     def select_options(self) -> list[str]:
#         """Return selection list."""
#         return [x.get("name", "") for x in self._device.chapters] if self._device.chapters else []
