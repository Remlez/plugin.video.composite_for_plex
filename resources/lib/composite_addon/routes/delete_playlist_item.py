# -*- coding: utf-8 -*-
"""

    Copyright (C) 2011-2018 PleXBMC (plugin.video.plexbmc) by hippojay (Dave Hawes-Johnson)
    Copyright (C) 2018-2019 Composite (plugin.video.composite_for_plex)

    This file is part of Composite (plugin.video.composite_for_plex)

    SPDX-License-Identifier: GPL-2.0-or-later
    See LICENSES/GPL-2.0-or-later.txt for more information.
"""

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from ..addon.common import CONFIG
from ..addon.common import PrintDebug
from ..addon.common import get_argv
from ..addon.common import i18n
from ..plex import plex

LOG = PrintDebug(CONFIG['name'])
PLEX_NETWORK = plex.Plex(load=False)


def run():
    PLEX_NETWORK.load()

    server_uuid = get_argv()[2]
    metadata_id = get_argv()[3]

    playlist_title = get_argv()[4]
    playlist_item_id = get_argv()[5]

    path = get_argv()[6]

    LOG.debug('Deleting playlist item at: %s' % playlist_item_id)

    server = PLEX_NETWORK.get_server_from_uuid(server_uuid)
    tree = server.get_metadata(metadata_id)

    item = tree[0]
    item_title = item.get('title', '')
    item_image = server.get_kodi_header_formatted_url(server.get_url_location() + item.get('thumb'))

    result = xbmcgui.Dialog().yesno(i18n('Confirm playlist item delete?'),
                                    i18n('Delete from the playlist?') %
                                    (item_title, playlist_title))
    if result:
        LOG.debug('Deleting....')
        response = server.delete_playlist_item(playlist_item_id, path)
        if response and not response.get('status'):
            xbmcgui.Dialog().notification(CONFIG['name'], i18n('has been removed the playlist') %
                                          (item_title, playlist_title), item_image)
            xbmc.executebuiltin('Container.Refresh')
            return

    xbmcgui.Dialog().notification(CONFIG['name'], i18n('Unable to remove from the playlist') %
                                  (item_title, playlist_title), item_image)
