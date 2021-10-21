# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

import sgtk
from sgtk.platform import Application

logger = sgtk.platform.get_logger(__name__)

__version__ = '0.0.03'

_third_mapping = {
    'nt': 'windows',
    'posix': 'linux'
}

resources_path = os.path.abspath(os.path.join(
    os.path.abspath(__file__),
    os.pardir,  # app location
    'resources'))

third_party = os.path.abspath(os.path.join(
    resources_path,
    'third-party',
    _third_mapping[os.name]
))


for sys_path in [third_party]:
    logger.info('Adding {} into sys.path'.format(sys_path))
    if sys_path not in sys.path:
        sys.path.append(sys_path)


class PlayblastBase(Application):
    """
    The playblast entry point. This class is responsible for initializing and tearing down
    the application, handle menu registration etc.
    """

    def init_app(self):
        """
        Called as the application is being initialized
        """

        # first, we use the special import_module command to access the playblast module
        # that resides inside the python folder in the playblast. This is where the actual UI
        # and business logic of the playblast is kept. By using the import_module command,
        # toolkit's code reload mechanism will work properly.
        app_payload = self.import_module("playblast")

        # now register a *command*, which is normally a menu entry of some kind on a Shotgun
        # menu (but it depends on the engine). The engine will manage this command and
        # whenever the user requests the command, it will call out to the callback.

        # first, set up our callback, calling out to a method inside the playblast module contained
        # in the python folder of the playblast
        menu_callback = lambda: app_payload.dialog.show_dialog(self,
                                                               __version__)

        # now register the command with the engine
        self.engine.register_command(self.get_setting("name", "Playblast..."),
                                     menu_callback)
