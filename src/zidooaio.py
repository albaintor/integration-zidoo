"""
Zidoo Remote Control API.

By Wizmo
References
    oem v1: https://www.zidoo.tv/Support/developer/
    oem v2: http://apidoc.zidoo.tv/s/98365225
"""

import asyncio
import json
import logging
import re
import socket
import struct
import urllib.parse
from asyncio import AbstractEventLoop, Lock, CancelledError
from datetime import datetime, timedelta, timezone
from enum import IntEnum, StrEnum
from functools import wraps
from typing import TypeVar, ParamSpec, Callable, Concatenate, Awaitable, Any, Coroutine

import ucapi
from aiohttp import ClientError, ClientSession, CookieJar
from config import DeviceInstance
from pyee.asyncio import AsyncIOEventEmitter
from ucapi.media_player import Attributes as MediaAttr, States
from ucapi.media_player import MediaType
from yarl import URL

SCAN_INTERVAL = timedelta(seconds=10)
SCAN_INTERVAL_RAPID = timedelta(seconds=1)
CONNECTION_RETRIES = 10


# pylint: disable = C0302


class Events(IntEnum):
    """Internal driver events."""

    CONNECTED = 0
    ERROR = 1
    UPDATE = 2
    IP_ADDRESS_CHANGED = 3
    DISCONNECTED = 4


_LOGGER = logging.getLogger(__name__)

VERSION = "0.3.2"
TIMEOUT = 5  # default timeout
TIMEOUT_INFO = 1  # for playing info
TIMEOUT_SEARCH = 10  # for searches
RETRIES = 3  # default retries
CONF_PORT = 9529  # default api port
DEFAULT_COUNT = 250  # default list limit
ZCMD_STATUS = "getPlayStatus"


class ZKEYS(StrEnum):
    """List of available keys."""

    ZKEY_BACK = "Key.Back"
    ZKEY_CANCEL = "Key.Cancel"
    ZKEY_HOME = "Key.Home"
    ZKEY_UP = "Key.Up"
    ZKEY_DOWN = "Key.Down"
    ZKEY_LEFT = "Key.Left"
    ZKEY_RIGHT = "Key.Right"
    ZKEY_OK = "Key.Ok"
    ZKEY_SELECT = "Key.Select"
    ZKEY_STAR = "Key.Star"
    ZKEY_POUND = "Key.Pound"
    ZKEY_DASH = "Key.Dash"
    ZKEY_MENU = "Key.Menu"
    ZKEY_MEDIA_PLAY = "Key.MediaPlay"
    ZKEY_MEDIA_STOP = "Key.MediaStop"
    ZKEY_MEDIA_PAUSE = "Key.MediaPause"
    ZKEY_MEDIA_NEXT = "Key.MediaNext"
    ZKEY_MEDIA_PREVIOUS = "Key.MediaPrev"
    ZKEY_NUM_0 = "Key.Number_0"
    ZKEY_NUM_1 = "Key.Number_1"
    ZKEY_NUM_2 = "Key.Number_2"
    ZKEY_NUM_3 = "Key.Number_3"
    ZKEY_NUM_4 = "Key.Number_4"
    ZKEY_NUM_5 = "Key.Number_5"
    ZKEY_NUM_6 = "Key.Number_6"
    ZKEY_NUM_7 = "Key.Number_7"
    ZKEY_NUM_8 = "Key.Number_8"
    ZKEY_NUM_9 = "Key.Number_9"
    ZKEY_USER_A = "Key.UserDefine_A"
    ZKEY_USER_B = "Key.UserDefine_B"
    ZKEY_USER_C = "Key.UserDefine_C"
    ZKEY_USER_D = "Key.UserDefine_D"
    ZKEY_MUTE = "Key.Mute"
    ZKEY_VOLUME_UP = "Key.VolumeUp"
    ZKEY_VOLUME_DOWN = "Key.VolumeDown"
    ZKEY_POWER_ON = "Key.PowerOn"
    ZKEY_MEDIA_BACKWARDS = "Key.MediaBackward"
    ZKEY_MEDIA_FORWARDS = "Key.MediaForward"
    ZKEY_INFO = "Key.Info"
    ZKEY_RECORD = "Key.Record"
    ZKEY_PAGE_UP = "Key.PageUP"
    ZKEY_PAGE_DOWN = "Key.PageDown"
    ZKEY_SUBTITLE = "Key.Subtitle"
    ZKEY_AUDIO = "Key.Audio"
    ZKEY_REPEAT = "Key.Repeat"
    ZKEY_MOUSE = "Key.Mouse"
    ZKEY_POPUP_MENU = "Key.PopMenu"
    ZKEY_APP_MOVIE = "Key.movie"
    ZKEY_APP_MUSIC = "Key.music"
    ZKEY_APP_PHOTO = "Key.photo"
    ZKEY_APP_FILE = "Key.file"
    ZKEY_LIGHT = "Key.light"
    ZKEY_RESOLUTION = "Key.Resolution"
    ZKEY_POWER_REBOOT = "Key.PowerOn.Reboot"
    ZKEY_POWER_OFF = "Key.PowerOn.Poweroff"
    ZKEY_POWER_STANDBY = "Key.PowerOn.Standby"
    ZKEY_PICTURE_IN_PICTURE = "Key.Pip"
    ZKEY_SCREENSHOT = "Key.Screenshot"
    ZKEY_APP_SWITCH = "Key.APP.Switch"


# Movie Player entry types
ZTYPE_VIDEO = 0
ZTYPE_MOVIE = 1
ZTYPE_COLLECTION = 2
ZTYPE_TV_SHOW = 3
ZTYPE_TV_SEASON = 4
ZTYPE_TV_EPISODE = 5
ZTYPE_OTHER = 6
ZTYPE_NAMES = {
    ZTYPE_VIDEO: "video",
    ZTYPE_MOVIE: "movie",
    ZTYPE_COLLECTION: "collection",
    ZTYPE_TV_SHOW: "tvshow",
    ZTYPE_TV_SEASON: "tvseason",
    ZTYPE_TV_EPISODE: "tvepisode",
    ZTYPE_OTHER: "other",
}

ZCONTENT_VIDEO = "Video Player"
ZCONTENT_MUSIC = "Music Player"
ZCONTENT_NONE = None

"""Movie Player search keys"""
ZVIDEO_FILTER_TYPES = {
    "all": 0,
    "favorite": 1,
    "watching": 2,
    "movie": 3,
    "tvshow": 4,
    "sd": 5,
    "bluray": 6,
    "4k": 7,
    "3d": 8,
    "children": 9,
    "recent": 10,
    "unwatched": 11,
    "other": 12,
    # ?"dolby": 13
}

ZVIDEO_SEARCH_TYPES = {
    # "all": -1,    # combined results
    "video": 0,  # all movies tvshows and collections
    "movie": 1,
    "tvshow": 2,
    "collection": 3,
}

ZMUSIC_SEARCH_TYPES = {"music": 0, "album": 1, "artist": 2, "playlist": 3}

"""File System devicce type names"""
ZDEVICE_FOLDER = 1000
ZDEVICE_NAMES = {
    1000: "hhd",
    1001: "usb",
    1002: "usb",
    1003: "tf",
    1004: "nfs",
    1005: "smb",
}

ZFILETYPE_NAMES = {
    0: "folder",
    1: "music",
    2: "movie",
    3: "Image",
    4: "txt",
    5: "apk",
    6: "pdf",
    7: "doc",
    8: "xls",
    9: "ppt",
    10: "web",
    11: "zip",
    # default: "other",
}

ZTYPE_MIMETYPE = {
    "image": 3,
    "video": 2,
    "audio": 2,  # 1 is Music Player but upnp needs dms server
    "other": 0,
    "default": 4,
    "application": 4,
}
ZUPNP_SERVERNAME = "zidoo-rc"

ZMEDIA_TYPE_ARTIST = "artist"
ZMEDIA_TYPE_ALBUM = "album"
ZMEDIA_TYPE_PLAYLIST = "playlist"

ZMUSIC_IMAGETYPE = {0: 0, 1: 1, 2: 0, 3: 0, 4: 1}
ZMUSIC_IMAGETARGET = {0: 16, 1: 16, 2: 32, 3: 16, 4: 32}
ZMUSIC_PLAYLISTTYPE = {
    ZMEDIA_TYPE_ARTIST: 3,
    ZMEDIA_TYPE_ALBUM: 4,
    ZMEDIA_TYPE_PLAYLIST: 5,
}

_ZidooDeviceT = TypeVar("_ZidooDeviceT", bound="ZidooRC")
_P = ParamSpec("_P")


def cmd_wrapper(
        func: Callable[Concatenate[_ZidooDeviceT, _P], Awaitable[dict[str, Any] | None]],
) -> Callable[Concatenate[_ZidooDeviceT, _P], Coroutine[Any, Any, ucapi.StatusCodes | None]]:
    """Catch command exceptions."""

    @wraps(func)
    async def wrapper(obj: _ZidooDeviceT, *args: _P.args, **kwargs: _P.kwargs) -> ucapi.StatusCodes:
        """Wrap all command methods."""
        res = await func(obj, *args, **kwargs)
        await obj.start_polling()
        if res and isinstance(res, dict):
            result: dict[str, Any] | None = res.get("result", None)
            if result and result.get("responseCode", None) == "0":
                return ucapi.StatusCodes.OK
            return ucapi.StatusCodes.BAD_REQUEST
        return ucapi.StatusCodes.OK

    return wrapper


class ZidooRC:
    """Zidoo Media Player Remote Control."""

    def __init__(
            self,
            host: str | None = None,
            device_config: DeviceInstance | None = None,
            psk: str = None,
            mac: str = None,
            loop: AbstractEventLoop | None = None,
    ) -> None:
        """Initialize the Zidoo class.

        Parameters
            host:
                IP address
            mac:
                address is optional and can be used to manually assign the WOL address.
            psk:
                authorization password key.  If not assigned, standard basic auth is used.
        """
        self._device_config = device_config
        self._mac = mac
        self._wifi_mac = None
        self._ethernet_mac = None
        if device_config:
            self.id = device_config.id
            self._ethernet_mac = device_config.net_mac_address
            self._wifi_mac = device_config.wifi_mac_address
            if host is None:
                host = device_config.address
        else:
            self.id = host
        self._event_loop = loop or asyncio.get_running_loop()
        self.events = AsyncIOEventEmitter(self._event_loop)
        self._source_list: dict[str, str] | None = None
        self._media_type: MediaType | None = None
        self._host = f"{host}:{CONF_PORT}"
        self._psk = psk
        self._session = None
        self._cookies = None
        self._content_mapping = []
        self._current_source: str | None = None
        self._app_list = {}
        self._power_status = False
        self._video_id = -1
        self._music_id = -1
        self._music_type = -1
        self._last_video_path = None
        self._movie_info = {}
        self._current_subtitle = 0
        self._current_audio = 0
        self._song_list = None
        self._state = States.OFF
        self._last_update = None
        self._last_state = States.OFF
        self._media_info = {}
        self._update_interval = SCAN_INTERVAL
        self._connect_lock = Lock()
        self._update_task = None
        self._update_lock = Lock()
        self._media_position_updated_at: datetime = datetime.now(timezone.utc)

    @property
    def state(self) -> States:
        """Return device state."""
        return self._state

    @property
    def attributes(self) -> dict[str, any]:
        """Return the device attributes."""
        self._media_position_updated_at = datetime.now(timezone.utc)
        updated_data = {
            MediaAttr.STATE: self.state,
            MediaAttr.MEDIA_POSITION: self.media_position if self.media_position else 0,
            MediaAttr.MEDIA_DURATION: self.media_duration if self.media_duration else 0,
            "media_position_updated_at": self.media_position_updated_at
        }
        if self.media_type:
            updated_data[MediaAttr.MEDIA_TYPE] = self.media_type
        if self.media_artist:
            updated_data[MediaAttr.MEDIA_ARTIST] = self.media_artist
        if self.media_title:
            updated_data[MediaAttr.MEDIA_TITLE] = self.media_title
        if self.media_album_name:
            updated_data[MediaAttr.MEDIA_ALBUM] = self.media_album_name
        if self.source:
            updated_data[MediaAttr.SOURCE] = self.source
        if self.source:
            updated_data[MediaAttr.SOURCE_LIST] = self.source_list
        if self.media_image_url:
            updated_data[MediaAttr.MEDIA_IMAGE_URL] = self.media_image_url
        return updated_data

    @property
    def media_type(self):
        """Return current media type."""
        return self._media_type

    @property
    def source(self) -> str:
        """Return the current input source."""
        return self._current_source

    @property
    def source_list(self) -> dict[str, str]:
        """List of available input sources."""
        return self._source_list

    @property
    def media_title(self):
        """Title of current playing media."""
        titles = []
        title = self._media_info.get("movie_name")
        if title is not None:
            titles.append(title)
        has_episode = False
        title = self._media_info.get("title")
        if title is not None:
            if title != self._media_info.get("movie_name"):
                titles.append(title)
            if re.search("S[0-9]+E[0-9]+", title) or re.search("S[0-9]+$", title):
                has_episode = True
        if not has_episode:
            if self._media_info.get("season") or self._media_info.get("episode"):
                episode = ""
                if self._media_info.get("season"):
                    episode = "S"+str(self._media_info.get("season"))
                if self._media_info.get("episode"):
                    episode += "E"+str(self._media_info.get("episode"))
                titles.append(episode)
        if len(titles) > 0:
            return " - ".join(titles)
        return ""

    @property
    def media_artist(self):
        """Artist of current playing media."""
        titles = []
        if self._media_info.get("episode_name"):
            titles.append(self._media_info.get("episode_name"))
        if self._media_info.get("season_name"):
            titles.append(self._media_info.get("season_name"))
        if self._media_info.get("artist"):
            titles.append(self._media_info.get("artist"))
        if len(titles) > 0:
            return " - ".join(titles)
        return ""

    @property
    def media_album_name(self):
        """Album of current playing media."""
        return self._media_info.get("album")

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        duration = self._media_info.get("duration")
        if duration:
            return float(duration) / 1000
        return None

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        position = self._media_info.get("position")
        if position:
            return float(position) / 1000
        return None

    @property
    def media_position_updated_at(self):
        """Return timestamp of urrent media position."""
        return self._media_position_updated_at.isoformat()

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        return self.generate_current_image_url()

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        if self._state == States.OFF:
            await self.turn_on()

    async def async_turn_off(self) -> None:
        """Turn off media player."""
        if self._state != States.OFF:
            await self.turn_off()

    @cmd_wrapper
    async def async_power_toggle(self) -> None:
        """Turn off media player."""
        if self._state != States.OFF:
            await self.turn_off()
        else:
            await self.turn_on()

    async def async_refresh_channels(self, force=True):
        """Update source list."""
        if not force and not self._source_list:
            sources = await self.load_source_list()
            self._source_list = [ZCONTENT_VIDEO, ZCONTENT_MUSIC]
            for key in sources:
                self._source_list.append(key)

    async def update(self) -> None:
        """Update data callback."""
        # pylint: disable = R0915,R1702
        if not self.is_connected():
            await self.connect()
        updated_data = {}
        # Retrieve the latest data.
        state = States.OFF
        media_type = MediaType.VIDEO
        try:
            if self.is_connected():
                state = States.PAUSED
                source_list = self._source_list
                await self.async_refresh_channels(force=False)
                if source_list != self._source_list:
                    updated_data[MediaAttr.SOURCE_LIST] = self.source_list
                # Save some data to check change later
                source = self._current_source
                image_url = self.generate_current_image_url()
                if image_url is None:
                    image_url = ""

                # Store current data to compare what's changed next
                title = self.media_title
                artist = self.media_artist
                album = self.media_album_name
                duration = self.media_duration
                position = self.media_position

                self._media_info = {}
                playing_info = await self.get_playing_info()
                if playing_info is None or not playing_info:
                    # self._media_type = MediaType.APP # None
                    media_type = MediaType.VIDEO
                    state = States.ON
                else:
                    self._media_info = playing_info
                    status = playing_info.get("status")
                    if status and status is not None:
                        if status == 1 or status is True:
                            state = States.PLAYING
                    mediatype = playing_info.get("source")
                    if mediatype and mediatype is not None:
                        if mediatype == "video":
                            item_type = self._media_info.get("type")
                            if item_type is not None and item_type == "tv":
                                media_type = MediaType.TVSHOW
                            else:
                                media_type = MediaType.MOVIE
                            self._current_source = ZCONTENT_VIDEO
                        else:
                            media_type = MediaType.MUSIC
                            self._current_source = ZCONTENT_MUSIC
                    else:
                        media_type = MediaType.VIDEO  # None
                    self._last_update = datetime.utcnow()

                if title != self.media_title:
                    updated_data[MediaAttr.MEDIA_TITLE] = self.media_title
                if album != self.media_album_name:
                    updated_data[MediaAttr.MEDIA_ALBUM] = self.media_album_name
                if artist != self.media_artist:
                    updated_data[MediaAttr.MEDIA_ARTIST] = self.media_artist
                if duration != self.media_duration:
                    updated_data[MediaAttr.MEDIA_DURATION] =  self.media_duration
                if position != self.media_position:
                    updated_data[MediaAttr.MEDIA_POSITION] = self.media_position
                if source != self.source:
                    updated_data[MediaAttr.SOURCE] = self.source
                new_image_url = self.generate_current_image_url()
                if new_image_url is None:
                    new_image_url = ""
                if new_image_url != image_url:
                    updated_data[MediaAttr.MEDIA_IMAGE_URL] = new_image_url
            if media_type != self._media_type:
                self._media_type = media_type
                updated_data[MediaAttr.MEDIA_TYPE] = self._media_type
        except Exception:  # pylint: disable=broad-except
            return

        if state != self._last_state:
            _LOGGER.debug("[%s] New state (%s)", self._host, state)
            self._last_state = state
            self._update_interval = (
                SCAN_INTERVAL if state == States.OFF else SCAN_INTERVAL_RAPID
            )
            updated_data[MediaAttr.STATE] = state
        self._state = state
        if updated_data:
            self.events.emit(Events.UPDATE, self.id, updated_data)

    def _jdata_build(self, method: str, params: dict = None) -> str:
        if params:
            ret = json.dumps(
                {"method": method, "params": [params], "id": 1, "version": "1.0"}
            )
        else:
            ret = json.dumps(
                {"method": method, "params": [], "id": 1, "version": "1.0"}
            )
        return ret

    async def _init_network(self):
        """Initialize network search on device."""
        # await self._req_json("ZidooFileControl/v2/searchUpnp")
        response = await self._req_json("ZidooFileControl/v2/getSavedSmbDevices")
        if response:
            # attempt connection to each saved network share
            data = response.get("data")
            if data and data["count"] > 0:
                for item in data["list"]:
                    url = urllib.parse.quote(item.get("url"), safe="")
                    await self._req_json(
                        f"ZidooFileControl/v2/getFiles?requestCount=100&startIndex=0&sort=0&url={url}"
                    )
        # gets current song list (and appears to initialize network shared on old devices)
        await self.get_music_playlist()
        # print(f"SONG_LIST: {self._song_list}")
        # _LOGGER.debug(response)
        # await self._req_json("ZidooFileControl/v2/getUpnpDevices")

    async def connect(self) -> json:
        """Connect to player and get authentication cookie.

        Returns
            json
                raw api response if successful.
        """
        # Don't do 2 connections at the same time, just wait the attempt to finish
        if self._connect_lock.locked():
            _LOGGER.debug("[%s] Connect already in process...", self._host)
            await self._connect_lock.acquire()
            response = await self.get_system_info(log_errors=False)
            self._connect_lock.release()
            return response

        await self._connect_lock.acquire()
        _LOGGER.debug("[%s] Connecting...", self._host)
        # /connect?uuid= requires authorization for each client
        # url = "ZidooControlCenter/connect?name={}&uuid={}&tag=0".format(client_name, client_uuid)
        # response = await self._req_json(url, log_errors=False)

        # pylint: disable = W0718
        try:
            response = await self.get_system_info(log_errors=False)

            if response and response.get("status") == 200:
                _LOGGER.debug("[%s] connected: %s", self._host, response)
                self._power_status = True
                await self._init_network()
                return response
            await self.start_polling()
        except Exception as ex:
            _LOGGER.error("[%s] Error during connection %s", self._host, ex)
        finally:
            self._connect_lock.release()

    async def disconnect(self) -> None:
        """Async Close connection."""
        await self.stop_polling()
        if self._session:
            await self._session.close()
        self._psk = None
        self._session = None

    async def start_polling(self):
        """Start polling task."""
        if self._update_task is not None:
            return
        _LOGGER.debug("[%s] Start polling task for device %s", self._host, self.id)
        self._update_task = self._event_loop.create_task(self._background_update_task())

    async def stop_polling(self):
        """Stop polling task."""
        if self._update_task:
            try:
                self._update_task.cancel()
            except CancelledError:
                pass
            self._update_task = None

    async def _background_update_task(self):
        self._reconnect_retry = 0
        while True:
            if not self._device_config.always_on:
                if self.state == States.OFF:
                    self._reconnect_retry += 1
                    if self._reconnect_retry > CONNECTION_RETRIES:
                        _LOGGER.debug("[%s] Stopping update task as the device %s is off", self._host,self.id)
                        break
                    _LOGGER.debug("[%s] Device %s is off, retry %s", self._host, self.id, self._reconnect_retry)
                elif self._reconnect_retry > 0:
                    self._reconnect_retry = 0
                    _LOGGER.debug("[%s] Device %s is on again", self._host, self.id)
            await self.update()
            await asyncio.sleep(10)

        self._update_task = None

    def is_connected(self) -> bool:
        """Check connection status.

        Returns
            bool
                True if connected.
        """
        return self._cookies is not None

    def _create_magic_packet(self, mac_address: str) -> bytes:
        addr_byte = mac_address.split(":")
        hw_addr = struct.pack(
            "BBBBBB",
            int(addr_byte[0], 16),
            int(addr_byte[1], 16),
            int(addr_byte[2], 16),
            int(addr_byte[3], 16),
            int(addr_byte[4], 16),
            int(addr_byte[5], 16),
        )
        return b"\xff" * 6 + hw_addr * 16

    def _wakeonlan(self) -> None:
        """Send WOL command. to known mac addresses."""
        messages = []
        if self._ethernet_mac is not None:
            messages.append(self._create_magic_packet(self._ethernet_mac))
        if self._wifi_mac is not None:
            messages.append(self._create_magic_packet(self._wifi_mac))
        if len(messages) > 0:
            socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            for msg in messages:
                socket_instance.sendto(msg, ("<broadcast>", 9))
            socket_instance.close()

    @cmd_wrapper
    async def send_key(self, key: str, log_errors: bool = False) -> bool:
        """Async Send Remote Control button command to device.

        Parameters
            key: str
                remote control key command (see ZKEY list)
            log_errors: bool
                suppresses error logging if False
        Returns
            True if successful
        """
        url = "ZidooControlCenter/RemoteControl/sendkey"
        params = {"key": key}

        response = await self._req_json(url, params, log_errors, max_retries=0)

        if response and response.get("status") == 200:
            return True
        return False

    async def _req_json(
            self,
            url: str,
            # pylint: disable = W0102
            params: dict = {},
            log_errors: bool = True,
            timeout: int = TIMEOUT,
            max_retries: int = RETRIES,
    ) -> json:
        """Async Send request command via HTTP json to player.

        Parameters
            url: str
                api call
            params: str
                api parameters
            log_errors: bool
                suppresses error logging if False
            max_retries
                reties on response errors
            timeout
                request timeout in seconds
        Returns
            json
                raw API response
        """
        while max_retries >= 0:
            response = await self._send_cmd(url, params, log_errors, timeout)

            if response and response.status == 200:
                result = await response.json(content_type=None)
                # _LOGGER.debug("url:%s params:%s result:%s",str(url),str(params),str(result.get("status")))
                if result:
                    # player can report 804 when switching media. force retry
                    if ZCMD_STATUS not in url or result.get("status") != 804:
                        return result

            if max_retries > 0:
                _LOGGER.warning("[W] Retry %d: url:%s", max_retries, url)
            max_retries -= 1

        # clear cookies to show not connected
        if self._cookies is not None:
            _LOGGER.debug("No response from player! Showing not connected")
            self._cookies = None

    async def _send_cmd(
            self,
            url: str,
            params: dict = None,
            log_errors: bool = True,
            timeout: int = TIMEOUT,
    ):
        """Async Send request command via HTTP json to player.

        Parameters
            url: str
                api call.
            params: str
                api parameters.
            log_errors: bool
                suppresses error logging if False
            timeout
                request timeout in seconds
        Returns
            response
                raw API response
        """
        if self._session is None:
            self._session = ClientSession(
                cookie_jar=CookieJar(unsafe=True, quote_cookie=False)
            )

        headers = {}
        if self._psk is not None:
            headers["X-Auth-PSK"] = self._psk

        headers["Cache-Control"] = "no-cache"
        headers["Connection"] = "keep-alive"

        url = f"http://{self._host}/{url}"

        try:
            response = await self._session.get(
                URL(url, encoded=True),
                params=params,
                cookies=self._cookies,
                timeout=timeout,
                headers=headers,
            )

        except ClientError as err:
            if log_errors and self._power_status:
                _LOGGER.info("[%s] Client Error: %s", self._host, str(err))

        except ConnectionError as err:
            if log_errors and self._power_status:
                _LOGGER.info("[%s] Connect Error: %s", self._host, str(err))

        except asyncio.exceptions.TimeoutError as err:
            if log_errors and self._power_status:
                _LOGGER.warning("[%s] Timeout Error: %s", self._host, str(err))

        else:
            if response is not None or response.status == 200:
                self._cookies = response.cookies
            return response

    async def get_source(self) -> str:
        """Async Return last known app."""
        return self._current_source

    async def load_source_list(self) -> dict[str, str]:
        """Async Return app list."""
        return await self.get_app_list()

    async def get_playing_info(self) -> json:
        """Async Get playing information of active app.

        Returns
            json (if successful)
                source: music = music player, video = vodeo player
                status: True if playing
                uri: path to current file
                title: title (filename)
                duration: length in ms
                position: position in ms
                artist: artist name(music only)
                track: track title (music only)
                type: ??
                movie_name: movie title (movie only)
                tag: tag line (movie only)
                date: release date (movie only)
                episode: episode number (tv only)
                episode_name: episode title (tv only)
                season: season number (tv only)
                season_name: season title (tv only)
                series_name: series title (tv only)
        """
        return_value = {}

        response = await self._get_video_playing_info()
        if response is not None:
            return_value = response
            return_value["source"] = "video"
            if return_value.get("status") is True:
                self._current_source = ZCONTENT_VIDEO
                return {**return_value, **self._movie_info}

        response = await self._get_music_playing_info()
        if response is not None:
            return_value = response
            return_value["source"] = "music"
            if return_value["status"] is True:
                self._current_source = ZCONTENT_MUSIC
                return return_value

        if not return_value:
            self._current_source = ZCONTENT_NONE

        return return_value

    async def _get_video_playing_info(self) -> json:
        """Async Get information from built in video player."""
        return_value = {}
        response = await self._req_json(
            "ZidooVideoPlay/" + ZCMD_STATUS, log_errors=False, timeout=TIMEOUT_INFO
        )

        if response is not None and response.get("status") == 200:
            if response.get("subtitle"):
                self._current_subtitle = response["subtitle"].get("index")
            if response.get("audio"):
                self._current_audio = response["audio"].get("index")
            if response.get("video"):
                result = response.get("video")
                return_value["status"] = result.get("status") == 1
                return_value["title"] = result.get("title")
                return_value["uri"] = result.get("path")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("currentPosition")
                return_value["width"] = result.get("width")
                return_value["height"] = result.get("height")
                return_value["fps"] = result.get("fps")
                return_value["bitrate"] = result.get("bitrate")
                return_value["audio"] = result.get("audioInfo")
                return_value["video"] = result.get("output")
                if (
                        return_value["status"] is True
                        and return_value["uri"]
                        and return_value["uri"] != self._last_video_path
                ):
                    self._last_video_path = return_value["uri"]
                    self._video_id = await self._get_id_from_uri(self._last_video_path)
                result = response.get("zoom")
                return_value["zoom"] = result.get("information")
                return return_value
        # _LOGGER.debug("video play info: %s", str(response))

    async def _get_id_from_uri(self, uri: str) -> int:
        """Async Return movie id from the path."""
        movie_id = 0
        movie_info = {}

        response = await self._req_json(
            f"ZidooPoster/v2/getAggregationOfFile?path={urllib.parse.quote(uri)}"
        )

        if response:
            movie_info["type"] = response.get("type")
            result = response.get("movie")
            if result is not None:
                movie_id = result.get("id")
                movie_info["movie_name"] = result.get("name")
                movie_info["tag"] = result["aggregation"].get("tagLine")
                release = result["aggregation"].get("releaseDate")
                if release:
                    movie_info["date"] = datetime.strptime(release, "%Y-%m-%d")
            result = response.get("episode")
            if result is not None:
                movie_id = result.get("id")
                movie_info["episode"] = result["aggregation"].get("episodeNumber")
                movie_info["episode_name"] = result["aggregation"].get("name")
            result = response.get("season")
            if result is not None:
                movie_info["season"] = result["aggregation"].get("seasonNumber")
                movie_info["season_name"] = result["aggregation"].get("name")
                movie_info["series_name"] = result["aggregation"].get("tvName")
            if not movie_id:
                result = response.get("video")
                if result is not None:
                    movie_id = result.get("parentId")

            self._movie_info = movie_info

        _LOGGER.debug("[%s] new media detected (%s): %s", self._host, str(movie_id), str(movie_info))
        return movie_id

    async def _get_music_playing_info(self) -> json:
        """Async Get information from built in Music Player."""
        return_value = {}
        response = await self._req_json(
            "ZidooMusicControl/" + ZCMD_STATUS, log_errors=False, timeout=TIMEOUT_INFO
        )

        # pylint: disable = W1405
        if response is not None and response.get("status") == 200:
            return_value["status"] = response.get("isPlay")
            result = response.get("music")
            if result is not None:
                return_value["title"] = result.get("title")
                return_value["artist"] = result.get("artist")
                return_value["track"] = result.get("number")
                return_value["date"] = result.get("date")
                return_value["uri"] = result.get("uri")
                return_value["bitrate"] = result.get("bitrate")
                return_value["audio"] = (
                    f"{result.get('extension')}: {result.get('channels')}"
                    f" channels {result.get('bits')} bits {result.get('SampleRate')} Hz"
                )
                self._music_id = result.get("id")
                self._music_type = result.get("type")

                result = response.get("state")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("position")

                result = response.get("state")
                if result is not None:
                    # update with satte - playing for newer firmware
                    return_value["status"] = result.get("playing")

                return return_value
        # _LOGGER.debug("music play info %s", str(response))

    async def _get_movie_playing_info(self) -> json:
        """Async Get information from built in Movie Player."""
        return_value = {}

        response = await self._req_json(
            "ZidooControlCenter/" + ZCMD_STATUS, log_errors=False, timeout=TIMEOUT_INFO
        )

        if response is not None and response.get("status") == 200:
            if response.get("file"):
                result = response.get("file")
                return_value["status"] = result.get("status") == 1
                return_value["title"] = result.get("title")
                return_value["uri"] = result.get("path")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("currentPosition")
                return return_value
        # _LOGGER.debug("movie play info {}".format(response))

    async def get_play_modes(self) -> json:
        """Async Get the play-mode list.

        Returns
            json
                raw api response when successful
        """
        response = await self._req_json("ZidooVideoPlay/getPlayModeList")

        if response is not None and response.get("status") == 200:
            return response

    def _next_data(self, data, index: int) -> int:
        """Toggle list."""
        temp = iter(data)
        for key in temp:
            if key == index:
                index = next(temp, 0)
                return index
        return 0

    async def get_subtitle_list(self, log_errors=True) -> dict:
        """Async Get subtitle list.

        Returns
            dictionary list
        """
        return_values = {}
        response = await self._req_json(
            "ZidooVideoPlay/getSubtitleList", log_errors=log_errors
        )

        if response is not None and response.get("status") == 200:
            for result in response["subtitles"]:
                index = result.get("index")
                return_values[index] = result.get("title")

        return return_values

    async def set_subtitle(self, index: int = None) -> bool:
        """Async Select subtitle.

        Parameters
            index: int
                subtitle list reference
        Return
            True if successful
        """
        if index is None:
            index = self._next_data(
                await self.get_subtitle_list(), self._current_subtitle
            )

        response = await self._req_json(
            f"ZidooVideoPlay/setSubtitle?index={index}", log_errors=False
        )

        if response is not None and response.get("status") == 200:
            self._current_subtitle = index
            return True
        return False

    async def get_audio_list(self) -> dict:
        """Async Get audio track list.

        Returns
            dictionary
                list of audio tracks
        """
        return_values = {}
        response = await self._req_json("ZidooVideoPlay/getAudioList")

        if response is not None and response.get("status") == 200:
            for result in response["subtitles"]:
                index = result.get("index")
                return_values[index] = result.get("title")

        return return_values

    async def set_audio(self, index: int = None) -> bool:
        """Async Select audio track.

        Parameters
            index: int
                audio track list reference
        Return
            True if successful
        """
        if index is None:
            index = self._next_data(await self.get_audio_list(), self._current_audio)

        response = await self._req_json(
            f"ZidooVideoPlay/setAudio?index={index}", log_errors=False
        )

        if response is not None and response.get("status") == 200:
            self._current_audio = index
            return True
        return False

    async def get_system_info(self, log_errors=True) -> json:
        """Async Get system information.

        Returns
            json is successful
                'status': 200
                'model': model name
                'ip': ip address
                'net_mac': wired mac address
                'wif_mac': wifi mac address
                'language': system language
                'firmware': firmware version
                'androidversion': os version
                'flash': flash/emmc memory size
                'ram':' ram memory size
                'ableRemoteSleep': network sleep compatible (buggy on Z9S)
                'ableRemoteReboot': network reboot compatible
                'ableRemoteShutdown': network shut down compatible
                'ableRemoteBoot': network boot compatible (wol)
                'pyapiversion': python api version
        """
        response = await self._req_json(
            "ZidooControlCenter/getModel", log_errors=log_errors, max_retries=0
        )

        if response and response.get("status") == 200:
            response["pyapiversion"] = VERSION
            return response

    async def get_power_status(self) -> str:
        """Async Get power status.

        Returns
            "on" when player is on
            "off" when player is not available
        """
        self._power_status = False
        try:
            response = await self.get_system_info()

            if response and response.get("status") == 200:
                self._power_status = True

        except Exception:  # pylint: disable=broad-except
            pass

        if self._power_status is True:
            return "on"
        return "off"

    async def get_volume_info(self):
        """Async Get volume info. Not currently supported."""
        # pylint: disable = W0613
        return None

    async def set_volume_level(self, volume):
        """Async Set volume level. Not currently supported."""
        # pylint: disable = W0613
        # api_volume = str(int(round(volume * 100)))
        return 0

    async def get_app_list(self, log_errors=True) -> dict[str, str]:
        """Async Get the list of installed apps.

        Results
            list of openable apps
                <app name>: <app_id>
        """
        return_values = {}

        response = await self._req_json(
            "ZidooControlCenter/Apps/getApps", log_errors=log_errors
        )

        if response is not None and response.get("status") == 200:
            for result in response["apps"]:
                if result.get("isCanOpen"):
                    name = result.get("label")
                    return_values[name] = result.get("packageName")

        return return_values

    async def start_app(self, app_name: str, log_errors=True) -> bool:
        """Async Start an app by name.

        Parameters
            app_name: str
                app list reference
        Return
            True if successful
        """
        if len(self._app_list) == 0:
            self._app_list = await self.get_app_list(log_errors)
        if app_name in self._app_list:
            return await self._start_app(self._app_list[app_name])
        return False

    async def _start_app(self, app_id) -> bool:
        """Async Start an app by package name."""
        response = await self._req_json(
            f"ZidooControlCenter/Apps/openApp?packageName={app_id}"
        )

        if response is not None and response.get("status") == 200:
            return True
        return False

    async def get_device_list(self) -> json:
        """Async Return list of root file system devices.

        Returns
            json device list if successful
                'name': device name
                'path': device path
                'type': device type (see ZDEVICE_TYPE)
        """
        response = await self._req_json("ZidooFileControl/getDevices")

        if response is not None and response.get("status") == 200:
            return response["devices"]

    async def get_movie_list(self, filter_type=-1, max_count=DEFAULT_COUNT) -> json:
        """Async Return list of movies.

        Parameters
            max_count: int
                maximum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """

        def by_id(e):
            return e["id"]

        if filter_type in ZVIDEO_FILTER_TYPES:
            filter_type = ZVIDEO_FILTER_TYPES.get(filter_type, None)

        # v2 http://{{host}}/Poster/v2/getAggregations?type=0&start=0&count=40
        response = await self._req_json(
            f"ZidooPoster/getVideoList?page=1&pagesize={max_count}&type={filter_type}"
        )

        if response is not None and response.get("status") == 200:
            if filter_type in {10, 11}:
                response["data"].sort(key=by_id, reverse=True)
            return response

    async def get_collection_list(self, movie_id) -> json:
        """Async Return video collection details.

        Parameters
            movie_id: int
                database movie_id
        Returns
            json
                raw API response if successful
        """
        response = await self._req_json(f"ZidooPoster/getCollection?id={movie_id}")

        if response is not None and response.get("status") == 200:
            return response

    async def get_movie_details(self, movie_id: int) -> json:
        """Async Return video details.

        Parameters
            movie_id: int
                database movie_id
        Returns
            json
                raw API response (no status)
        """
        # v1 response = self._req_json("ZidooPoster/getDetail?id={}".format(movie_id))
        response = await self._req_json(f"Poster/v2/getDetail?id={movie_id}")

        if response is not None:  # and response.get("status") == 200:
            return response

    async def get_episode_list(self, season_id: int) -> json:
        """Async Return video list sorted by episodes.

        Parameters
            movie_id: int
                database movie_id
        Returns
            json:
                raw API episode list if successful
        """

        def by_episode(e):
            return e["aggregation"]["episodeNumber"]

        response = await self.get_movie_details(season_id)

        if response is not None:
            episodes = response.get("aggregations")
            if episodes is None:
                # try alternative location
                result = response.get("aggregation")
                if result is not None:
                    episodes = result.get("aggregations")

            if episodes is not None:
                episodes.sort(key=by_episode)
                return episodes

    async def _collection_video_id(self, movie_id: int) -> int:
        """Async Get collection id for movie."""
        response = await self.get_collection_list(movie_id)

        if response is not None:
            for result in response["data"]:
                if result["type"] == 0:
                    return result["aggregationId"]
        return movie_id

    async def get_music_list(
            self, music_type: int = 0, music_id: int = None, max_count: int = DEFAULT_COUNT
    ) -> json:
        """Async Return list of music.

        Parameters
            max_count: int
                maximum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """
        if music_type == ZMEDIA_TYPE_ARTIST:
            return await self._get_artist_list(music_id, max_count)
        if music_type == ZMEDIA_TYPE_ALBUM:
            return await self._get_album_list(music_id, max_count)
        if music_type == ZMEDIA_TYPE_PLAYLIST:
            return await self._get_playlist_list(music_id, max_count)
        return await self._get_song_list(max_count)

    async def _get_song_list(self, max_count: int = DEFAULT_COUNT) -> json:
        """Async Return list of albums or album music.

        Parameters
            max_count: int
                maximum number of list items
        Returns
            json
                raw API response if successful
        """
        response = await self._req_json(
            f"MusicControl/v2/getSingleMusics?start=0&count={max_count}"
        )
        self._song_list = self._get_music_ids(response.get("array"))

        if response is not None:
            return response

    async def _get_album_list(
            self, album_id: int = None, max_count: int = DEFAULT_COUNT
    ) -> json:
        """Async Return list of albums or album music.

        Parameters
            album_id: int or str
                see ZVIDEO_FILTER_TYPE
            max_count: int
                maximum number of list items
        Returns
            json
                raw API response if successful
        """
        if album_id:
            response = await self._req_json(
                f"MusicControl/v2/getAlbumMusics?id={album_id}&start=0&count={max_count}"
            )
        else:
            response = await self._req_json(
                f"MusicControl/v2/getAlbums?start=0&count={max_count}"
            )

        if response is not None:
            return response

    async def _get_artist_list(
            self, artist_id: int = None, max_count: int = DEFAULT_COUNT
    ) -> json:
        """Async Return list of artists or artist music.

        Parameters
            artist_id: int
                artist id
            max_count: int
                maximum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """
        if artist_id:
            response = await self._req_json(
                f"MusicControl/v2/getArtistMusics?id={artist_id}&start=0&count={max_count}"
            )
        else:
            response = await self._req_json(
                f"MusicControl/v2/getArtists?start=0&count={max_count}"
            )

        if response is not None:  # and response.get("status") == 200:
            return response

    async def _get_playlist_list(self, playlist_id=None, max_count=DEFAULT_COUNT):
        """Async Return list of playlists.

        Parameters
            max_count: int
                maximum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """
        if playlist_id:
            if playlist_id == "playing":
                response = await self._req_json(
                    f"MusicControl/v2/getPlayQueue?start=0&count={max_count}"
                )
                if response:
                    self._song_list = self._get_music_ids(response.get("array"))
            else:
                response = await self._req_json(
                    f"MusicControl/v2/getSongListMusics?id={playlist_id}&start=0&count={max_count}"
                )
        else:
            response = await self._req_json(
                # "MusicControl/v2/getSongList?start=0&count={}".format(max_count)
                "MusicControl/v2/getSongLists"
            )

        if response is not None:
            return response

    async def search_movies(
            self, search_type: int | str = 0, max_count: int = DEFAULT_COUNT
    ) -> json:
        """Async Return list of video based on query.

        Parameters
            movie_id: int
                database movie_id
            search_type: int ot str
                see ZVIDEO_SEARCH_TYPES
        Returns
            json
                raw API response (no status)
        """
        if search_type in ZVIDEO_SEARCH_TYPES:
            search_type = ZVIDEO_SEARCH_TYPES.get(search_type, 0)

        # v1 "ZidooPoster/search?q={}&type={}&page=1&pagesize={}".format(query, filter_type, max_count)
        response = await self._req_json(
            f"Poster/v2/searchAggregation?q={max_count}&type={search_type}&start=0&count={max_count}",
            timeout=TIMEOUT_SEARCH,
        )

        if response is not None and response.get("status") == 200:
            return response

    async def search_music(
            self,
            query: str,
            search_type: int | str = 0,
            max_count: int = DEFAULT_COUNT,
            play: bool = False,
    ) -> json:
        """Async Return list of music based on query.

        Parameters
            query: str
                text to search
            search_type: int or str
                see ZMUSIC_SEARCH_TYPES
            max_count: int
                max number of songs returned
            play: bool
                automatically plays content.  search_type=0 only
        Returns
            json
                raw API response (no status)
        """
        if search_type in ZMUSIC_SEARCH_TYPES:
            search_type = ZMUSIC_SEARCH_TYPES.get(search_type, 0)

        if search_type == 1:
            return await self._search_album(query, max_count)
        if search_type == 2:
            return await self._search_artist(query, max_count)
        response = await self._search_song(query, max_count)
        if response:
            self._song_list = self._get_music_ids(response.get("array"), sub="result")
            if play and self._song_list:
                await self.play_music(media_type="music", music_id=self._song_list[0])
        return response

    async def _search_song(self, query: str, max_count: int = DEFAULT_COUNT) -> json:
        """Async Search by song title.

        Parameters
            query: str
                text to search
        Returns
            json
                raw API response (no status)
        """
        response = await self._req_json(
            f"MusicControl/v2/searchMusic?key={query}&start=0&count={max_count}",
            timeout=TIMEOUT_SEARCH,
        )

        if response is not None:
            return response

    async def _search_album(self, query: str, max_count: int = DEFAULT_COUNT) -> json:
        """Async Search by album name.

        Parameters
            query: str
                text to search
        Returns
            json
                raw API response (no status)
        """
        response = await self._req_json(
            f"MusicControl/v2/searchAlbum?key={query}&start=0&count={max_count}",
            timeout=TIMEOUT_SEARCH,
        )

        if response is not None:
            return response

    async def _search_artist(self, query: str, max_count: int = DEFAULT_COUNT) -> json:
        """Async Search by artist name.

        Parameters
            query: str
                text to search
        Returns
            json
                raw API response (no status)
        """
        response = await self._req_json(
            f"MusicControl/v2/searchArtist?key={query}&start=0&count={max_count}",
            timeout=TIMEOUT_SEARCH,
        )

        if response is not None:
            return response

    async def play_file(self, uri: str) -> bool:
        """Async Play content by URI.

        Parameters
            uri: str
                path of file to play
        Returns
            True if successful
        """
        url = f"ZidooFileControl/openFile?path={uri}&videoplaymode={0}"
        # has issues with parsing for local files

        response = await self._req_json(url)

        if response and response.get("status") == 200:
            return True
        return False

    async def play_stream(self, uri: str, media_type) -> bool:
        """Async Play url by type.

        Uses undocumented v2 upnp FileOpen calls using 'res' and 'type'
            res: str
                quoted url
            type : int or str
                mime type or see ZTYPE_MIMETYPE
            other information parameters can be used
                name: str (title?)
                date: datetime
                resolution: <width>x<height>
                bitrate: int (audio?)
                size: int (duration?)
                channels: int (audio?)
                bitRates: int (audio?)
                way: {0,1,2,3} (play mode?)
                album: str
                number: int (audio)
                sampleRates: int (audio)
                albumArt: url (audio)
        Parameters:
            uri: str
                uri link to stream
            media_type: int
                See ZTYPE_MIMETYPE
        Returns
            True if successful
        """
        # pylint: disable = W1405
        # take major form mime type
        if isinstance(media_type, str) and "/" in media_type:
            media_type = media_type.split("/")[0]

        if media_type in ZTYPE_MIMETYPE:
            media_type = ZTYPE_MIMETYPE.get(media_type)

        # the res uri needs to be double quoted to protect keys etc.
        # use safe='' in quote to force "/" quoting
        uri = urllib.parse.quote(uri, safe="")

        upnp = f"upnp://{ZUPNP_SERVERNAME}/{VERSION}?type={media_type}&res={uri}"
        url = f"ZidooFileControl/v2/openFile?url={urllib.parse.quote(upnp, safe='')}"
        _LOGGER.debug("[%s] Stream command %s", self._host, str(url))

        response = await self._req_json(url)

        if response and response.get("code") == 0:
            return True
        return False

    async def play_movie(self, movie_id: int, video_type: int = -1) -> bool:
        """Async Play video content by Movie id.

        Parameters
            movie_id
                database id
        Returns
            True if successful
        """
        # uses the agreggateid to find the first video to play
        if video_type != 0:
            movie_id = await self._collection_video_id(movie_id)
        # print("Video id : {}".format(video_id))

        # v2 http://{}/VideoPlay/playVideo?index=0
        response = await self._req_json(
            f"ZidooPoster/PlayVideo?id={movie_id}&type={video_type}"
        )

        if response and response.get("status") == 200:
            return True
        return False

    def _get_music_ids(self, data, key="id", sub=None):
        ids = []
        if data:
            for item in data:
                result = item.get(sub) if sub else item
                if result:
                    _id = result.get(key)
                    ids.append(str(_id))
        return ids

    async def play_music(
            self, media_id: int = None, media_type: int = "music", music_id: int = None
    ) -> bool:
        """Async Play video content by id.

        Parameters
            media_id
                database id for media type (or ids for music type)
            media_type
                see ZMUSIC_SEARCH_TYPE
            music_id
                database id for track to play (use None or -1 for first)
        Returns
            True if successfull
        """
        # pylint: disable = W1405
        if media_type in ZMUSIC_PLAYLISTTYPE and media_id != "playing":
            response = await self._req_json(
                f"MusicControl/v2/playMusic?type={ZMUSIC_PLAYLISTTYPE[media_type]}"
                f"&id={media_id}&musicId={music_id}&music_type=0&trackIndex=1&sort=0"
            )
        else:  # music
            response = await self._req_json(
                f"MusicControl/v2/playMusics?ids={'%2C'.join(self._song_list)}&musicId={music_id}&trackIndex=-1"
            )

        if response and response.get("status") == 200:
            return True
        return False

    async def get_video_playlist(self) -> json:
        """Async Return the current video playlist.

        Returns
            json if successful
                'status': 200
                'size': count
                'playList' : array
                    'title': video name (file name)
                    'index': int
        """
        response = await self._req_json("VideoPlay/getPlaylist")

        if response and response.get("status") == 200:
            return response

    async def get_music_playlist(self, max_count: int = DEFAULT_COUNT) -> json:
        """Async Get current music player playlist.

        Parameters
            max_count: int
                list size limit
        Returns
            raw api response if successful
        """
        response = await self._req_json(
            f"MusicControl/v2/getPlayQueue?start=0&count={max_count}"
        )

        if response is not None:
            return response

    async def get_file_list(self, uri: str, file_type: int = 0) -> json:
        """Async Return file list in hass format.

        Returns
            json if successful
                'status':200
                'isExists':True
                'perentPath':'/storage/356d9775-8a40-4d4e-8ef9-9eea931fc5ae'
                'filelist': list
                    'name': file name
                    'type': file type
                    'path': full file path
                    'isBDMV': True if ?high definition
                    'isBluray': True if blue ray resolution
                    'length': length in ms
                    'modifyDate': linux date code
        """
        response = await self._req_json(
            f"ZidooFileControl/getFileList?path={uri}&type={file_type}"
        )

        if response is not None and response.get("status") == 200:
            return response

    async def get_host_list(self, uri: str, host_type: int = 1005) -> json:
        """Async Return host list of saved network shares.

        Returns
            json if successful
                'status':200
                'filelist': list
                    'name': host/share name
                    'type': file type
                    'path': full file path
                    'isBDMV': True if ?high definition
                    'isBluray': True if blue ray resolution
                    'length': length in ms
                    'modifyDate': linux date code
        """
        response = await self._req_json(
            f"ZidooFileControl/getHost?path={uri}&type={host_type}"
        )
        _LOGGER.debug("zidoo host list: %s", str(response))

        return_value = {}
        share_list = []
        if response is not None and response.get("status") == 200:
            return_value["status"] = 200
            hosts = response["hosts"]
            for item in hosts:
                response = await self.get_file_list(item.get("ip"), item.get("type"))
                hostname = item.get("name").split("/")[-1]
                if response is not None and response.get("status") == 200:
                    for share in response["filelist"]:
                        share["name"] = hostname + "/" + share.get("name")
                        share_list.append(share)
        return_value["filelist"] = share_list
        return return_value

    def generate_image_url(
            self, media_id: int, media_type: int, width: int = 400, height: int = None
    ) -> str:
        """Get link to thumbnail."""
        if media_type in ZVIDEO_SEARCH_TYPES:
            if height is None:
                height = width * 3 / 2
            return self._generate_movie_image_url(media_id, width, height)
        if media_type in ZMUSIC_SEARCH_TYPES:
            if height is None:
                height = width
            return self._generate_music_image_url(
                media_id, ZMUSIC_SEARCH_TYPES[media_type], width, height
            )
        return None

    def _generate_movie_image_url(
            self, movie_id: int, width: int = 400, height: int = 600
    ) -> str:
        """Get link to thumbnail.

        Parameters
            movie_id: int
                database id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
        """
        # http://{}/Poster/v2/getPoster?id=66&w=60&h=30
        url = f"http://{self._host}/ZidooPoster/getFile/getPoster?id={movie_id}&w={width}&h={height}"

        return url

    # pylint: disable = W0613
    def _generate_music_image_url(
            self, music_id: int, music_type: int = 0, width: int = 200, height: int = 200
    ) -> str:
        """Get link to thumbnail.

        Parameters
            music_id: int
                dtanabase id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
        """
        url = (
            f"http://{self._host}/ZidooMusicControl/v2/getImage?id={music_id}"
            f"&music_type={ZMUSIC_IMAGETYPE[music_type]}"
            f"&type={music_type}&target={ZMUSIC_IMAGETARGET[music_type]}"
        )

        return url

    def generate_current_image_url(self, width: int = 1080, height: int = 720) -> str:
        """Get link to artwork.

        Parameters
            movie_id: int
                database id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
        """
        url = None

        if self._current_source == ZCONTENT_VIDEO and self._video_id > 0:
            url = f"http://{self._host}/ZidooPoster/getFile/getBackdrop?id={self._video_id}&w={width}&h={height}"

        if self._current_source == ZCONTENT_MUSIC and self._music_id > 0:
            url = (
                f"http://{self._host}/ZidooMusicControl/v2/getImage?"
                f"id={self._music_id}&music_type={self._music_type}&type=4&target=16"
            )

        # _LOGGER.debug("zidoo getting current image: url-{}".format(url))
        return url

    async def turn_on(self):
        """Async Turn the media player on."""
        # Try using the power on command incase the WOL doesn't work
        self._wakeonlan()
        # ZKEYS.ZKEY_POWER_ON will actually turn off the device, not needed
        # return await self._send_key(ZKEYS.ZKEY_POWER_ON, False)
        return True

    @cmd_wrapper
    async def turn_off(self, standby=False):
        """Async Turn off media player."""
        return await self.send_key(
            ZKEYS.ZKEY_POWER_STANDBY if standby else ZKEYS.ZKEY_POWER_OFF
        )

    @cmd_wrapper
    async def volume_up(self):
        """Async Volume up the media player."""
        return await self.send_key(ZKEYS.ZKEY_VOLUME_UP)

    @cmd_wrapper
    async def volume_down(self):
        """Async Volume down media player."""
        return await self.send_key(ZKEYS.ZKEY_VOLUME_DOWN)

    @cmd_wrapper
    async def mute_volume(self):
        """Async Send mute command."""
        return self.send_key(ZKEYS.ZKEY_MUTE)

    @cmd_wrapper
    async def media_play_pause(self):
        """Async Send play or Pause command."""
        if self.state == States.PLAYING:
            return await self.media_pause()
        return await self.media_play()

    @cmd_wrapper
    async def media_play(self) -> any:
        """Async Send play command."""
        # self._send_key(ZKEYS.ZKEY_OK)
        if self._current_source == ZCONTENT_NONE and self._last_video_path:
            return await self.play_file(self._last_video_path)
        if self._current_source == ZCONTENT_MUSIC:
            return await self._req_json("MusicControl/v2/playOrPause")
        return await self.send_key(ZKEYS.ZKEY_MEDIA_PLAY)

    @cmd_wrapper
    async def media_pause(self):
        """Async Send media pause command to media player."""
        if self._current_source == ZCONTENT_MUSIC:
            return await self._req_json("MusicControl/v2/playOrPause")
        return await self.send_key(ZKEYS.ZKEY_MEDIA_PAUSE)

    @cmd_wrapper
    async def media_stop(self):
        """Async Send media pause command to media player."""
        return await self.send_key(ZKEYS.ZKEY_MEDIA_STOP)

    @cmd_wrapper
    async def media_next_track(self):
        """Async Send next track command."""
        if self._current_source == ZCONTENT_MUSIC:
            return await self._req_json("MusicControl/v2/playNext")
        return await self.send_key(ZKEYS.ZKEY_MEDIA_NEXT)

    @cmd_wrapper
    async def media_previous_track(self):
        """Async Send the previous track command."""
        if self._current_source == ZCONTENT_MUSIC:
            return await self._req_json("MusicControl/v2/playLast")
        await self.send_key(ZKEYS.ZKEY_MEDIA_PREVIOUS)

    @cmd_wrapper
    async def set_media_position(self, position):
        """Async Set the current playing position.

        Parameters
            position
                position in ms
        Return
            True if successful
        """
        response = None
        if self._current_source == ZCONTENT_VIDEO:
            response = await self._set_movie_position(position)
        elif self._current_source == ZCONTENT_MUSIC:
            response = await self._set_audio_position(position)

        if response is not None:
            return True
        return False

    async def _set_movie_position(self, position):
        """Async Set current position for video player."""
        response = await self._req_json(
            f"ZidooVideoPlay/seekTo?positon={int(position)}"
        )

        if response is not None and response.get("status") == 200:
            return response

    async def _set_audio_position(self, position):
        """Async Set current position for music player."""
        response = await self._req_json(
            f"ZidooMusicControl/seekTo?time={int(position)}"
        )

        if response is not None and response.get("status") == 200:
            return response
