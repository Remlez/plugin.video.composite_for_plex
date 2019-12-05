# -*- coding: utf-8 -*-
"""

    Copyright (C) 2011-2018 PleXBMC (plugin.video.plexbmc) by hippojay (Dave Hawes-Johnson)
    Copyright (C) 2018-2019 Composite (plugin.video.composite_for_plex)

    This file is part of Composite (plugin.video.composite_for_plex)

    SPDX-License-Identifier: GPL-2.0-or-later
    See LICENSES/GPL-2.0-or-later.txt for more information.
"""

import xbmcgui  # pylint: disable=import-error

from ..addon.common import CONFIG
from ..addon.common import SETTINGS
from ..addon.common import PrintDebug
from ..addon.common import i18n
from ..addon.utils import get_master_server
from ..plex import plex

LOG = PrintDebug(CONFIG['name'])
PLEX_NETWORK = plex.Plex(load=False)


def run():
    PLEX_NETWORK.load()
    servers = get_master_server(all_servers=True, plex_network=PLEX_NETWORK)
    LOG.debug(str(servers))

    current_master = SETTINGS.get_setting('masterServer')

    display_option_list = []
    for address in servers:
        found_server = address.get_name()
        if found_server == current_master:
            found_server = found_server + '*'
        display_option_list.append(found_server)

    result = xbmcgui.Dialog().select(i18n('Select master server'), display_option_list)
    if result == -1:
        return

    LOG.debug('Setting master server to: %s' % servers[result].get_name())
    SETTINGS.update_master_server(servers[result].get_name())