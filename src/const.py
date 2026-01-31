"""Constants for Zidoo component."""

import logging
from enum import Enum, StrEnum

from ucapi.media_player import MediaType

_LOGGER = logging.getLogger(__package__)


class ZidooSensors(str, Enum):
    """Sensors."""

    SENSOR_AUDIO_STREAM = "sensor_audio_stream"
    SENSOR_SUBTITLE_STREAM = "sensor_subtitle_stream"
    SENSOR_CHAPTER = "sensor_chapter"
    SENSOR_VIDEO_INFO = "sensor_video_info"
    SENSOR_AUDIO_INFO = "sensor_audio_info"
    SENSOR_VOLUME = "sensor_volume"
    SENSOR_VOLUME_MUTED = "sensor_volume_muted"


class ZidooSelects(str, Enum):
    """Selects."""

    SELECT_AUDIO_STREAM = "select_audio_stream"
    SELECT_SUBTITLE_STREAM = "select_subtitle_stream"
    SELECT_CHAPTER = "select_chapter"


DOMAIN = "zidoo"
DATA_ZIDOO_CONFIG = "zidoo_config"
VERSION = "1.1.1"
DATA = "data"
UPDATE_TRACK = "update_track"
UPDATE_LISTENER = "update_listener"

MANUFACTURER = "Zidoo"

CLIENTID_PREFIX = "home-assistant"
CLIENTID_NICKNAME = "Home Assistant"

CONF_SHORTCUT = "shortcut_json"
CONF_POWERMODE = "powermode"

SUBTITLE_SERVICE = "set_subtitle"
AUDIO_SERVICE = "set_audio"
BUTTON_SERVICE = "send_key"

# Triggers
EVENT_TURN_ON = "zidoo.turn_on"
EVENT_TURN_OFF = "zidoo.turn_off"

MEDIA_TYPE_FILE = "file"

ZSHORTCUTS = [
    {"name": "FAVORITES", "path": "favorite", "type": MediaType.VIDEO},
    {"name": "LATEST", "path": "recent", "type": MediaType.VIDEO, "default": True},
    {"name": "WATCHING", "path": "watching", "type": MediaType.VIDEO},
    {"name": "SD", "path": "sd", "type": MediaType.VIDEO},
    {"name": "DISC", "path": "bluray", "type": MediaType.VIDEO},
    {"name": "UHD", "path": "4k", "type": MediaType.VIDEO},
    {"name": "3D", "path": "3d", "type": MediaType.VIDEO},
    {"name": "KIDS", "path": "children", "type": MediaType.VIDEO},
    {"name": "UNWATCHED", "path": "unwatched", "type": MediaType.VIDEO},
    {"name": "OTHER", "path": "other", "type": MediaType.VIDEO},
    {"name": "ALL", "path": "all", "type": MediaType.VIDEO},
    {"name": "MOVIES", "path": "movie", "type": MediaType.MOVIE, "default": True},
    {"name": "TV SHOWS", "path": "tvshow", "type": MediaType.TVSHOW, "default": True},
    {"name": "MUSIC", "path": "music", "type": MediaType.MUSIC, "default": True},
    {"name": "ALBUMS", "path": "album", "type": MediaType.MUSIC},
    {"name": "ARTISTS", "path": "artist", "type": MediaType.MUSIC},
    {"name": "PLAYLISTS", "path": "playlist", "type": MediaType.MUSIC},
]
ZDEFAULT_SHORTCUTS = ["recent", "movie", "tvshow"]


ZCONTENT_ITEM_TYPE = {
    0: MEDIA_TYPE_FILE,  # folder
    1: MediaType.MUSIC,  # music
    2: MediaType.VIDEO,  # video
    # 3: MediaType.IMAGE,  # image
    # 4: 'text',
    # 5: 'apk',
    # 6: 'pdf',
    # 7: 'document',
    # 8: 'spreadsheet',
    # 9: 'presentation',
    # 10: 'web',
    # 11: 'archive' ,
    # 12: 'other'
    1000: MEDIA_TYPE_FILE,  # hhd
    1001: MEDIA_TYPE_FILE,  # usb
    1002: MEDIA_TYPE_FILE,  # usb
    1003: MEDIA_TYPE_FILE,  # tf
    # 1004: MediaType.URL,  # nfs
    # 1005: MediaType.URL,  # smb
    1006: MEDIA_TYPE_FILE,
    1007: MEDIA_TYPE_FILE,
    1008: MEDIA_TYPE_FILE,
}

# ZTYPE_MEDIA_CLASS = {
#     ZTYPE_VIDEO: MediaClass.VIDEO,
#     ZTYPE_MOVIE: MediaClass.MOVIE,
#     ZTYPE_COLLECTION: MediaClass.MOVIE,
#     ZTYPE_TV_SHOW: MediaClass.TV_SHOW,
#     ZTYPE_TV_SEASON: MediaClass.SEASON,
#     ZTYPE_TV_EPISODE: MediaClass.TRACK,  # MediaClass.EPISODE, # no episode images with zidoo
#     6: MediaClass.TRACK,  # Other
#     7: MediaClass.TRACK,  # Dummy for +1
# }

# ZTYPE_MEDIA_TYPE = {
#     ZTYPE_VIDEO: MediaType.VIDEO,
#     ZTYPE_MOVIE: MediaType.MOVIE,
#     ZTYPE_COLLECTION: MediaType.MOVIE,
#     ZTYPE_TV_SHOW: MediaType.TVSHOW,
#     ZTYPE_TV_SEASON: MediaType.SEASON,
#     ZTYPE_TV_EPISODE: MediaType.EPISODE,  # no episode images with zidoo
#     ZTYPE_OTHER: MediaType.TRACK,
#     7: MediaType.TRACK,  # Dummy for +1
# }


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
