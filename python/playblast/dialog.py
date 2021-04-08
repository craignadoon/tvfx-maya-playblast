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
import threading
# import maya.cmds as cmds
import pprint

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog
from .playblast import PlayblastManager

# sg frameworks
# shotgun_fields = sgtk.platform.import_framework("tk-framework-qtwidgets", "shotgun_fields")
# context_selector = sgtk.platform.import_framework("tk-framework-qtwidgets", "context_selector")
# playback_label = sgtk.platform.import_framework("tk-framework-qtwidgets", "playback_label")
# shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")
# task_manager = sgtk.platform.import_framework("tk-framework-shotgunutils", "task_manager")

logger = sgtk.platform.get_logger(__name__)

def show_dialog(app_instance, entity_type, entity_ids, version_str='0.0.1'):
    """
    Shows the main dialog window, using the special Shotgun multi-select mode.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 
    
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    AppDialog.__version__ = version_str
    app_instance.engine.show_dialog("Maya Playblast: v{}".format(version_str),  # window title
                                    app_instance,                               # playblast instance
                                    AppDialog,                 # window class to instantiate
                                    entity_type,               # arguments to pass to constructor
                                    entity_ids)


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """

    def __init__(self, entity_type, entity_ids):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()
        self._app.logger.debug("$$$$ self._app = {}".format(self._app))
        # tk = self._app.tk
        # self._app.logger.info("tk instance = {}".format(tk))
        self.context = None

        self.pbMngr = PlayblastManager(self._app,self.context)
        self.setDefaultUiData()
        self._app.logger.info("$$$$ setDefaultUiData DONE ")

        # self._app.logger.info("$$$$ self.pbMngr.getContext() = {}".format(self.pbMngr.getContext()))
        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk 

        # logging happens via a standard toolkit logger
        self._app.logger.info("Track's maya playblast")

        # lastly, set up our very basic UI
        self.ui.context.setText("Current selection type: %s, <br>Currently selected ids: %s" % (entity_type, entity_ids))
        self.ui.createPlayblast.clicked.connect(self.doPlayblast)

    def setDefaultUiData(self):
        try:
            # FRAME RANGE: from maya scene
            startFrame, endFrame = self.pbMngr.getFrameRange()
            self._app.logger.info("setDefaultUiData: startFrame, endFrame = {0}, {1}".format(startFrame, endFrame))
            self.ui.frameRange_start.setText(str(startFrame))
            self.ui.frameRange_end.setText(str(endFrame))

            # SCALE:
            self.ui.lineEdit_scale.setText(str('0.50'))

            # FRAME PADDING: how many frames before the start frame
            self.ui.lineEdit_framePadding.setText(str('4'))

            # RESOLUTION : (hard coding for now)
            self.ui.lineEdit_finalRes_w.setText(str('960'))
            self.ui.lineEdit_finalRes_h.setText(str('540'))

            # FORMAT: default playblast format is set to movie as of now
            self.ui.cb_format.setCurrentText(self.ui.cb_format.keys().index('avi'))
            self.ui.cb_encoding.setCurrentText(self.ui.cb_encoding.keys().index('None'))
            #self.appExeCB.setCurrentIndex(self.items.keys().index('Maya Executable'))
            #text = str(combobox1.currentText())

            # self.ui.lineEdit_focalLength
            # self.ui.cb_passType
            # comment
            self.ui.textEdit_comment.setText(str("playblast for {will shot give context}"))
        except:
            self._app.logger.debug("Could not set the ui defaults -_-")

    def gatherUiData(self):
        #change the encoding as per format choice
        if str(self.ui.cb_format.currentText()) == "image":
            encoding = 'jpeg'
        else:
            #if str(self.ui.cb_format.currentText) == "avi":
            encoding = 'None'

        playblastParams = {
            'startTime': int(self.ui.frameRange_start.text()),
            'endTime': int(self.ui.frameRange_end.text()),
            'filename': self.pbMngr.formatOutputPath(),
            'forceOverwrite': True,
            'format': str(self.ui.cb_format.currentText()),
            'percent': float(self.ui.lineEdit_scale.text()) * 100,
            #'compression': 'H.264',
            'width': int(float(self.ui.lineEdit_finalRes_w.text())),
            'height': int(float(self.ui.lineEdit_finalRes_h.text())),
            'offScreen': True,
            # 'quality': 70,
            # 'viewer': True,
            'framePadding': int(self.ui.lineEdit_framePadding.text()),
            'compression': encoding
        }
        self._app.logger.debug("playblastParams gathered: ")
        self._app.logger.debug(playblastParams)
        pprint.pprint(playblastParams)
        return playblastParams

    def doPlayblast(self):
        # if self.ui.createPlayblast.clicked():
        #     createPlayblast.clicked.connect(createPlayblast)
        temp_directory = "C:/work/tempPlayblast"
        # make sure it is exists
        if not os.path.isdir(temp_directory):
            os.mkdir(temp_directory)

        overridePlayblastParams = {}
        overridePlayblastParams = self.gatherUiData()

        filename = "C:/work/tempPlayblast/mayaplayblast.mov"
        # playblastfile = self.createPlayblast(filename)
        playblastFile = self.pbMngr.createPlayblast(filename, overridePlayblastParams)
        self._app.logger.info("Playblast created = {}".format(playblastFile))

        self.pbMngr.uploadToShotgun(playblastFile)

        # uploadToShotgun = self._ui.chbUploadToShotgun.isChecked()
        # self.setUploadToShotgun(uploadToShotgun)
        #
        # showViewer = self._ui.chbShowViewer.isChecked()
        # overridePlayblastParams["viewer"] = showViewer
        #
        # percentInt = self._ui.cmbPercentage.itemData( self._ui.cmbPercentage.currentIndex() )
        # overridePlayblastParams["percent"] = percentInt
        # self._handler.doPlayblast(**overridePlayblastParams)
    #
    # def createPlayblast(self, filename, **kwargs):
    #
    #     filename = "C:/work/tempPlayblast/mayaplayblast.mov"
    #     playblastParams = {
    #                         'filename': filename,
    #                         'offScreen': True,
    #                         'percent': 50,
    #                         'quality': 70,
    #                         'viewer': True,
    #                         'width': 960,
    #                         'height': 540,
    #                         'framePadding': 4,
    #                         # 'format': 'image',
    #                         'format': 'avi',
    #                         #'encoding': 'none',
    #                         # 'compression': 'H.264',
    #                         'forceOverwrite': True,
    #                         }
    #     playblastParams.update(kwargs)
    #
    #     # if not self.focus:
    #     #     self.focus = True
    #     print "in playblast.py before creating playblast"
    #     resultPlayblastPath = cmds.playblast(**playblastParams)
    #     print "in playblast.py before return"
    #     return resultPlayblastPath