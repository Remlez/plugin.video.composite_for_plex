# -*- coding: utf-8 -*-
"""

    Copyright (C) 2013-2019 PleXBMC Helper (script.plexbmc.helper)
        by wickning1 (aka Nick Wing), hippojay (Dave Hawes-Johnson)
    Copyright (C) 2019 Composite (plugin.video.composite_for_plex)

    This file is part of Composite (plugin.video.composite_for_plex)

    SPDX-License-Identifier: GPL-2.0-or-later
    See LICENSES/GPL-2.0-or-later.txt for more information.
"""

import base64
import json

from six import PY3

from kodi_six import xbmc  # pylint: disable=import-error

from .http_persist import RequestManager
from ..addon.constants import CONFIG
from ..addon.logger import Logger
from ..addon.settings import AddonSettings

LOG = Logger()
SETTINGS = AddonSettings()


def kodi_photo():
    return 'photo'


def kodi_video():
    return 'video'


def kodi_audio():
    return 'audio'


def plex_photo():
    return 'photo'


def plex_video():
    return 'video'


def plex_audio():
    return 'music'


def kodi_type(_plex_type):
    if _plex_type == plex_photo():
        return kodi_photo()
    if _plex_type == plex_video():
        return kodi_video()
    if _plex_type == plex_audio():
        return kodi_audio()
    return None


def plex_type(_kodi_type):
    if _kodi_type == kodi_photo():
        return plex_photo()
    if _kodi_type == kodi_video():
        return plex_video()
    if _kodi_type == kodi_audio():
        return plex_audio()
    return None


def get_platform():  # pylint: disable=too-many-return-statements
    if xbmc.getCondVisibility('system.platform.osx'):
        return 'MacOSX'
    if xbmc.getCondVisibility('system.platform.atv2'):
        return 'AppleTV2'
    if xbmc.getCondVisibility('system.platform.ios'):
        return 'iOS'
    if xbmc.getCondVisibility('system.platform.windows'):
        return 'Windows'
    if xbmc.getCondVisibility('system.platform.raspberrypi'):
        return 'RaspberryPi'
    if xbmc.getCondVisibility('system.platform.linux'):
        return 'Linux'
    if xbmc.getCondVisibility('system.platform.android'):
        return 'Android'
    return 'Unknown'


def jsonrpc(action, arguments=None):
    """ put some JSON together for the JSON-RPC APIv6 """
    if arguments is None:
        arguments = {}

    if action.lower() == 'sendkey':
        request = json.dumps({
            'jsonrpc': '2.0',
            'method': 'Input.SendText',
            'params': {
                'text': arguments[0],
                'done': False
            }
        })
    elif action.lower() == 'ping':
        request = json.dumps({
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'JSONRPC.Ping'
        })
    elif action.lower() == 'playmedia':
        full_url = arguments[0]
        resume = arguments[1]
        xbmc.Player().play('plugin://plugin.video.composite_for_plex/?mode=5&force=' +
                           resume + '&url=' + full_url)
        return True
    elif arguments:
        request = json.dumps({
            'id': 1,
            'jsonrpc': '2.0',
            'method': action,
            'params': arguments
        })
    else:
        request = json.dumps({
            'id': 1,
            'jsonrpc': '2.0',
            'method': action
        })

    LOG.debugplus('Sending request to Kodi without network stack: %s' % request)
    result = parse_jsonrpc(xbmc.executeJSONRPC(request))

    if not result:
        web_server = SETTINGS.kodi_web_server()
        make_web_request = web_server['name'] and web_server['password'] and web_server['port']

        if make_web_request:
            # xbmc.executeJSONRPC appears to fail on the login screen, but going
            # through the network stack works, so let's try the request again
            credentials = '%s:%s' % (web_server['name'], web_server['password'])
            if PY3:
                credentials = credentials.encode('utf-8')
                base64bytes = base64.encodebytes(credentials)
                base64string = base64bytes.decode('utf-8').replace('\n', '')
            else:
                base64string = base64.encodestring(credentials).replace('\n', '')  # pylint: disable=deprecated-method
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + base64string,
            }
            result = parse_jsonrpc(RequestManager().post('127.0.0.1', web_server['port'],
                                                         '/jsonrpc', request, headers))

    return result


def parse_jsonrpc(json_raw):
    if not json_raw:
        LOG.debug('Empty response from Kodi')
        return {}

    LOG.debugplus('Response from Kodi: %s' % json_raw)
    parsed = json.loads(json_raw)
    if parsed.get('error', False):
        LOG.debug('Kodi returned an error: %s' % parsed.get('error'))
    return parsed.get('result', {})


def get_xml_header():
    return '<?xml version="1.0" encoding="utf-8"?>' + '\r\n'


def get_ok_message():
    return get_xml_header() + '<Response code="200" status="OK" />'


def get_plex_headers():
    client_details = SETTINGS.companion_receiver()
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Access-Control-Allow-Origin': '*',
        'X-Plex-Version': CONFIG['version'],
        'X-Plex-Client-Identifier': client_details['uuid'],
        'X-Plex-Provides': 'player',
        'X-Plex-Product': CONFIG['name'],
        'X-Plex-Device-Name': client_details['name'],
        'X-Plex-Platform': 'Kodi',
        'X-Plex-Model': get_platform(),
        'X-Plex-Device': 'PC',
    }
    myplex_user = SETTINGS.get_setting('myplex_user')
    if myplex_user:
        headers['X-Plex-Username'] = myplex_user
    return headers


def get_players():
    info = jsonrpc('Player.GetActivePlayers') or []
    ret = {}
    for player in info:
        player['player_id'] = int(player['playerid'])
        del player['playerid']
        ret[player['type']] = player
    return ret


def get_player_ids():
    ret = []
    for player in get_players().values():
        ret.append(player['player_id'])
    return ret


def get_video_player_id(players=None):
    if players is None:
        players = get_players()
    return players.get(kodi_video(), {}).get('player_id', None)


def get_audio_player_id(players=None):
    if players is None:
        players = get_players()
    return players.get(kodi_audio(), {}).get('player_id', None)


def get_photo_player_id(players=None):
    if players is None:
        players = get_players()
    return players.get(kodi_photo(), {}).get('player_id', None)


def get_volume():
    return str(jsonrpc('Application.GetProperties', {
        'properties': ['volume']
    }).get('volume', 100))


def time_to_millis(time):
    return ((time['hours'] * 3600 + time['minutes'] * 60 + time['seconds'])
            * 1000 + time['milliseconds'])


def millis_to_time(millis):
    millis = int(millis)
    seconds = millis / 1000
    minutes = seconds / 60
    hours = minutes / 60
    seconds = seconds % 60
    minutes = minutes % 60
    millis = millis % 1000
    return {
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'milliseconds': millis
    }


def text_from_xml(element):
    return element.firstChild.data