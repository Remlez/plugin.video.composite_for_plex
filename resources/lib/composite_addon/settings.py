"""

    Copyright (C) 2011-2018 PleXBMC (plugin.video.plexbmc) by hippojay (Dave Hawes-Johnson)
    Copyright (C) 2018-2019 Composite (plugin.video.composite_for_plex)

    This file is part of Composite (plugin.video.composite_for_plex)

    SPDX-License-Identifier: GPL-2.0-or-later
    See LICENSES/GPL-2.0-or-later for more information.
"""

import json

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from six.moves import range


class AddonSettings:

    def __init__(self, addon_id):
        self.addon_id = addon_id
        self.settings = xbmcaddon.Addon(addon_id)
        try:
            self.addon_name = self.settings.getAddonInfo('name').decode('utf-8')
        except AttributeError:
            self.addon_name = self.settings.getAddonInfo('name')
        xbmc.log(self.addon_name + '.settings -> Reading settings configuration', xbmc.LOGDEBUG)
        self.stream = self.settings.getSetting('streaming')

    def open_settings(self):
        return self.settings.openSettings()

    def get_setting(self, name, fresh=False):
        if fresh:
            value = xbmcaddon.Addon(self.addon_id).getSetting(name)
        else:
            value = self.settings.getSetting(name)

        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            return value

    def get_debug(self):
        return int(self.get_setting('debug'))

    def set_setting(self, name, value):
        if isinstance(value, bool):
            value = str(value).lower()

        self.settings.setSetting(name, value)

    def get_wakeservers(self):
        wakeserver = []
        for servers in list(range(1, 12)):
            wakeserver.append(self.settings.getSetting('wol%s' % servers))
        return wakeserver

    def get_stream(self):
        return self.stream

    def set_stream(self, value):
        self.stream = value

    def dump_settings(self):
        return self.__dict__

    def update_master_server(self, value):
        xbmc.log(self.addon_name + '.settings -> Updating master server to %s' % value, xbmc.LOGDEBUG)
        self.settings.setSetting('masterServer', '%s' % value)

    def use_up_next(self):
        upnext_id = 'service.upnext'
        s_upnext_enabled = self.get_setting('use_up_next', fresh=True)

        try:
            _ = xbmcaddon.Addon(upnext_id)
            has_upnext = True
            upnext_disabled = False
        except RuntimeError:
            addon_xml = xbmc.translatePath('special://home/addons/%s/addon.xml' % upnext_id)
            if xbmcvfs.exists(addon_xml):  # if addon.xml exists, add-on is disabled
                has_upnext = True
                upnext_disabled = True
            else:
                has_upnext = False
                upnext_disabled = False

        if s_upnext_enabled and has_upnext and upnext_disabled:
            enable_upnext = xbmcgui.Dialog().yesno(self.addon_name, self.settings.getLocalizedString(30688))
            if enable_upnext:
                upnext_disabled = not self.enable_addon(upnext_id)

        if (not has_upnext or upnext_disabled) and s_upnext_enabled:
            self.set_setting('use_up_next', False)
            return False

        return s_upnext_enabled and has_upnext and not upnext_disabled

    def addon_status(self, addon_id):
        request = {
            "jsonrpc": "2.0",
            "method": "Addons.GetAddonDetails",
            "id": 1,
            "params": {
                "addonid": "%s" % addon_id,
                "properties": ["enabled"]
            }
        }
        response = xbmc.executeJSONRPC(json.dumps(request))
        response = json.loads(response)
        try:
            is_enabled = response['result']['addon']['enabled'] is True
            xbmc.log(self.addon_name + '.settings -> %s is %s' %
                     (addon_id, 'enabled' if is_enabled else 'disabled'), xbmc.LOGDEBUG)
            return is_enabled
        except KeyError:
            xbmc.log(self.addon_name + '.settings -> addon_status received an unexpected response', xbmc.LOGERROR)
            return False

    def disable_addon(self, addon_id):
        request = {
            "jsonrpc": "2.0",
            "method": "Addons.SetAddonEnabled",
            "params": {
                "addonid": "%s" % addon_id,
                "enabled": False
            },
            "id": 1
        }

        xbmc.log(self.addon_name + '.settings -> disabling %s' % addon_id, xbmc.LOGDEBUG)
        response = xbmc.executeJSONRPC(json.dumps(request))
        response = json.loads(response)
        try:
            return response['result'] == 'OK'
        except KeyError:
            xbmc.log(self.addon_name + '.settings -> disable_addon received an unexpected response', xbmc.LOGERROR)
            return False

    def enable_addon(self, addon_id):
        request = {
            "jsonrpc": "2.0",
            "method": "Addons.SetAddonEnabled",
            "params": {
                "addonid": "%s" % addon_id,
                "enabled": True
            },
            "id": 1
        }

        xbmc.log(self.addon_name + '.settings -> enabling %s' % addon_id, xbmc.LOGDEBUG)

        response = xbmc.executeJSONRPC(json.dumps(request))
        response = json.loads(response)
        try:
            return response['result'] == 'OK'
        except KeyError:
            xbmc.log(self.addon_name + '.settings -> enable_addon received an unexpected response', xbmc.LOGERROR)
            return False
