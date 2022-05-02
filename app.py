#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ============================================================================
# Copyright (C) 2021 Track Visual Effects LTD, All Rights Reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Track Visual Effects LTD, which is
# protected by IP Protection law.
#
# Author: rdevarkonda@trackvfx.com
# Module: app.py
# ============================================================================
"""Playblast app
"""

import sgtk
from sgtk.platform import Application

logger = sgtk.platform.get_logger(__name__)

__version__ = '0.0.09'


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

    def create_playblast_manager(self):
        return self.import_module('playblast').PlayblastManager(
            self, self.engine.context)
