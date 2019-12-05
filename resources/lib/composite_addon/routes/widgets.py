# -*- coding: utf-8 -*-
"""

    Copyright (C) 2019 Composite (plugin.video.composite_for_plex)

    This file is part of Composite (plugin.video.composite_for_plex)

    SPDX-License-Identifier: GPL-2.0-or-later
    See LICENSES/GPL-2.0-or-later.txt for more information.
"""

import xbmcplugin  # pylint: disable=import-error

from ..addon.common import MODES
from ..addon.common import SETTINGS
from ..addon.common import get_handle
from ..addon.common import i18n
from ..addon.utils import create_gui_item
from ..plex import plex

PLEX_NETWORK = plex.Plex(load=False)


def run(url):
    PLEX_NETWORK.load()

    server = PLEX_NETWORK.get_server_from_url(url)

    sections = server.get_sections()

    items = []
    for section in sections:
        if section.is_movie():
            details = {
                'title': '%s: %s' % (server.get_name(), i18n('Movies on Deck'))
            }
            extra_data = {
                'mode': MODES.TXT_MOVIES_ON_DECK,
                'parameters': {
                    'server_uuid': server.get_uuid()
                }
            }
            items.append(create_gui_item(section.get_path(), details, extra_data))

            details = {
                'title': '%s: %s' % (server.get_name(), i18n('Recently Added Movies'))
            }
            extra_data = {
                'mode': MODES.TXT_MOVIES_RECENT_ADDED,
                'parameters': {
                    'server_uuid': server.get_uuid()
                }
            }
            items.append(create_gui_item(section.get_path(), details, extra_data))

            details = {
                'title': '%s: %s' % (server.get_name(), i18n('Recently Released Movies'))
            }
            extra_data = {
                'mode': MODES.TXT_MOVIES_RECENT_RELEASE,
                'parameters': {
                    'server_uuid': server.get_uuid()
                }
            }
            items.append(create_gui_item(section.get_path(), details, extra_data))

        if section.is_show():
            details = {
                'title': '%s: %s' % (server.get_name(), i18n('TV Shows on Deck'))
            }
            extra_data = {
                'mode': MODES.TXT_TVSHOWS_ON_DECK,
                'parameters': {
                    'server_uuid': server.get_uuid()
                }
            }
            items.append(create_gui_item(section.get_path(), details, extra_data))

            details = {
                'title': '%s: %s' % (server.get_name(), i18n('Recently Added TV Shows'))
            }
            extra_data = {
                'mode': MODES.TXT_TVSHOWS_RECENT_ADDED,
                'parameters': {
                    'server_uuid': server.get_uuid()
                }
            }
            items.append(create_gui_item(section.get_path(), details, extra_data))

            details = {
                'title': '%s: %s' % (server.get_name(), i18n('Recently Aired TV Shows'))
            }
            extra_data = {
                'mode': MODES.TXT_TVSHOWS_RECENT_AIRED,
                'parameters': {
                    'server_uuid': server.get_uuid()
                }
            }
            items.append(create_gui_item(section.get_path(), details, extra_data))

    if items:
        xbmcplugin.addDirectoryItems(get_handle(), items, len(items))
    xbmcplugin.endOfDirectory(get_handle(), cacheToDisc=SETTINGS.get_setting('kodicache'))