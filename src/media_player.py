"""
Media-player entity functions.

:copyright: (c) 2026 by Albaintor
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from typing import Any

from ucapi import EntityTypes, MediaPlayer, StatusCodes
from ucapi.media_player import (
    Attributes,
    BrowseOptions,
    BrowseResults,
    Commands,
    DeviceClasses,
    Features,
)
from ucapi.media_player import MediaContentType as MediaContent
from ucapi.media_player import (
    Options,
    SearchResults,
    States,
)
from ucapi.msg_definitions import SearchOptions

from config import ConfigDevice, ZidooEntity, create_entity_id

# from const import MediaSearchFilter
from zidooaio import ZKEYS, ZidooClient

_LOG = logging.getLogger(__name__)

SIMPLE_COMMANDS = [
    ZKEYS.ZKEY_POWER_STANDBY,
    ZKEYS.ZKEY_POWER_REBOOT,
    ZKEYS.ZKEY_CANCEL,
    ZKEYS.ZKEY_MEDIA_STOP,
    ZKEYS.ZKEY_APP_MOVIE,
    ZKEYS.ZKEY_APP_FILE,
    ZKEYS.ZKEY_APP_MUSIC,
    ZKEYS.ZKEY_APP_PHOTO,
    ZKEYS.ZKEY_RESOLUTION,
    ZKEYS.ZKEY_REPEAT,
    ZKEYS.ZKEY_PICTURE_IN_PICTURE,
    ZKEYS.ZKEY_SELECT,
    ZKEYS.ZKEY_LIGHT,
]


class ZidooMediaPlayer(ZidooEntity, MediaPlayer):
    """Representation of a Sony Media Player entity."""

    def __init__(self, config_device: ConfigDevice, device: ZidooClient):
        """Initialize the class."""
        self._device = device
        self._config_device = config_device

        entity_id = create_entity_id(config_device.id, EntityTypes.MEDIA_PLAYER)
        features = [
            Features.ON_OFF,
            Features.TOGGLE,
            Features.VOLUME_UP_DOWN,
            Features.MUTE_TOGGLE,
            Features.SELECT_SOURCE,
            Features.HOME,
            Features.MEDIA_TITLE,
            Features.MEDIA_ARTIST,
            Features.MEDIA_ALBUM,
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
            Features.SEEK,
            "play_media",  # TODO : replace when UC library updated
            # "clear_playlist",
            "browse_media",
            "search_media",
            "search_media_classes",
        ]
        attributes = {
            Attributes.STATE: States.UNAVAILABLE,
            Attributes.SOURCE: "",
            Attributes.SOURCE_LIST: [],
            Attributes.MEDIA_IMAGE_URL: "",
            Attributes.MEDIA_TITLE: "",
            Attributes.MEDIA_ALBUM: "",
            Attributes.MEDIA_ARTIST: "",
            Attributes.MEDIA_POSITION: 0,
            Attributes.MEDIA_DURATION: 0,
            Attributes.MEDIA_TYPE: MediaContent.VIDEO,
            "media_id": None,
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
            options={Options.SIMPLE_COMMANDS: SIMPLE_COMMANDS},
        )

    @property
    def deviceid(self) -> str:
        """Return the device identifier."""
        return self._config_device.id

    async def command(
        self,
        cmd_id: str,
        params: dict[str, Any] | None = None,
        *,
        websocket: Any,
    ) -> StatusCodes:
        """
        Media-player entity command handler.

        Called by the integration-API if a command is sent to a configured media-player entity.

        :param cmd_id: command
        :param params: optional command parameters
        :return: status code of the command request
        """
        # pylint: disable = R0915
        _LOG.info("Got %s command request: %s %s", self.id, cmd_id, params)

        if self._device is None:
            _LOG.warning("No device instance for entity: %s", self.id)
            return StatusCodes.SERVICE_UNAVAILABLE

        match cmd_id:
            case Commands.VOLUME_UP:
                res = await self._device.volume_up()
            case Commands.VOLUME_DOWN:
                res = await self._device.volume_down()
            case Commands.MUTE_TOGGLE:
                res = await self._device.mute_volume()
            case Commands.ON:
                await self._device.turn_on()
                return StatusCodes.OK
            case Commands.OFF:
                res = await self._device.turn_off()
            case Commands.TOGGLE:
                res = await self._device.power_toggle()
            case Commands.SELECT_SOURCE:
                res = await self._device.start_app(params.get("source", ""))
            case Commands.NEXT:
                res = await self._device.media_next_track()
            case Commands.PREVIOUS:
                res = await self._device.media_previous_track()
            case Commands.CHANNEL_UP:
                res = await self._device.send_key(ZKEYS.ZKEY_PAGE_UP)
            case Commands.CHANNEL_DOWN:
                res = await self._device.send_key(ZKEYS.ZKEY_PAGE_DOWN)
            case Commands.PLAY_PAUSE:
                res = await self._device.media_play_pause()
            case Commands.STOP:
                res = await self._device.media_stop()
            case Commands.FAST_FORWARD:
                res = await self._device.send_key(ZKEYS.ZKEY_MEDIA_FORWARDS)
            case Commands.REWIND:
                res = await self._device.send_key(ZKEYS.ZKEY_MEDIA_BACKWARDS)
            case Commands.RECORD:
                res = await self._device.send_key(ZKEYS.ZKEY_RECORD)
            case Commands.CURSOR_UP:
                res = await self._device.send_key(ZKEYS.ZKEY_UP)
            case Commands.CURSOR_DOWN:
                res = await self._device.send_key(ZKEYS.ZKEY_DOWN)
            case Commands.CURSOR_LEFT:
                res = await self._device.send_key(ZKEYS.ZKEY_LEFT)
            case Commands.CURSOR_RIGHT:
                res = await self._device.send_key(ZKEYS.ZKEY_RIGHT)
            case Commands.CURSOR_ENTER:
                res = await self._device.send_key(ZKEYS.ZKEY_OK)
            case Commands.BACK:
                res = await self._device.send_key(ZKEYS.ZKEY_BACK)
            case Commands.MENU:
                res = await self._device.send_key(ZKEYS.ZKEY_MENU)
            case Commands.HOME:
                res = await self._device.send_key(ZKEYS.ZKEY_HOME)
            case Commands.SETTINGS:
                res = await self._device.send_key(ZKEYS.ZKEY_APP_SWITCH)
            case Commands.CONTEXT_MENU:
                res = await self._device.send_key(ZKEYS.ZKEY_POPUP_MENU)
            case Commands.INFO:
                res = await self._device.send_key(ZKEYS.ZKEY_INFO)
            case Commands.AUDIO_TRACK:
                res = await self._device.send_key(ZKEYS.ZKEY_AUDIO)
            case Commands.SUBTITLE:
                res = await self._device.send_key(ZKEYS.ZKEY_SUBTITLE)
            case Commands.SEEK:
                res = await self._device.set_media_position(params.get("media_position", 0) * 1000)
            case Commands.DIGIT_0:
                res = await self._device.send_key(ZKEYS.ZKEY_NUM_0)
            case Commands.DIGIT_1:
                res = await self._device.send_key(ZKEYS.ZKEY_NUM_1)
            case Commands.DIGIT_2:
                res = await self._device.send_key(ZKEYS.ZKEY_NUM_2)
            case Commands.DIGIT_3:
                res = await self._device.send_key(ZKEYS.ZKEY_NUM_3)
            case Commands.DIGIT_4:
                res = await self._device.send_key(ZKEYS.ZKEY_NUM_4)
            case Commands.DIGIT_5:
                res = await self._device.send_key(ZKEYS.ZKEY_NUM_5)
            case Commands.DIGIT_6:
                res = await self._device.send_key(ZKEYS.ZKEY_NUM_6)
            case Commands.DIGIT_7:
                res = await self._device.send_key(ZKEYS.ZKEY_NUM_7)
            case Commands.DIGIT_8:
                res = await self._device.send_key(ZKEYS.ZKEY_NUM_8)
            case Commands.DIGIT_9:
                res = await self._device.send_key(ZKEYS.ZKEY_NUM_9)
            case Commands.PLAY_MEDIA:
                res = await self._device.play_media(params if params else {})
            # case Commands.CLEAR_PLAYLIST:  # TODO
            #   res = await self._device.clear_playlist()
            case _:
                return StatusCodes.NOT_IMPLEMENTED

        if res:
            return StatusCodes.OK
        return StatusCodes.BAD_REQUEST

    async def browse(self, options: BrowseOptions) -> BrowseResults | StatusCodes:
        """
        Execute entity browsing request.

        Returns NOT_IMPLEMENTED if no handler is installed.

        :param options: browsing parameters
        :return: browsing response or status code if any error occurs
        """
        _LOG.debug("[%s] Browse media request %s", self._device.device_config.address, options)
        browse_media_item, paging = await self._device.browse_media(
            None, options.media_id, options.media_type, options.paging
        )
        return BrowseResults(media=browse_media_item, pagination=paging)

    async def search(self, options: SearchOptions) -> SearchResults | StatusCodes:
        """
        Execute media search request.

        Returns NOT_IMPLEMENTED if no handler is installed.

        :param options: search parameters
        :return: search response or status code if any error occurs
        """
        _LOG.debug("[%s] Search media request %s", self._device.device_config.address, options)
        if options.query is None:
            return StatusCodes.BAD_REQUEST
        browse_media_item, paging = await self._device.browse_media(
            options.query, options.media_id, options.media_type, options.paging
        )
        return SearchResults(media=browse_media_item.items, pagination=paging)

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
            state = update[Attributes.STATE]
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
            "media_position_updated_at",
            "media_id",
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
                attributes["media_position_updated_at"] = ""

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
