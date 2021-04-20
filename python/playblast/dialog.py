# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.


import pprint

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog
from .playblast import PlayblastManager

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
        self.context = None

        self.pbMngr = PlayblastManager(self._app,self.context)
        self.setDefaultUiData()
        self._app.logger.info("$$$$ setDefaultUiData DONE ")

        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk 

        # logging happens via a standard toolkit logger
        self._app.logger.info("Track's maya playblast")

        # lastly, set up our very basic UI
        # self.ui.context.setText("Current selection type: %s, <br>Currently selected ids: %s" % (entity_type, entity_ids))
        self.ui.createPlayblast.clicked.connect(self.doPlayblast)

    def setDefaultUiData(self):
        """
        method to set defaults in ui to minimize user input.
        :return:
        """
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
            # self.ui.cb_encoding.setCurrentText(self.ui.cb_encoding.keys().index('None'))

            # description
            comment_entity, comment_project = self.pbMngr.getContext()
            # self.ui.textEdit_comment.setText("playblast for {0}, {1}".format(comment_entity, comment_project))
            self.ui.textEdit_comment.setPlainText("playblast for {0}, {1}".format(comment_entity, comment_project))
            self._app.logger.debug("setDefaultUiData: playblast for {0}, {1}".format(comment_entity, comment_project))
            # pass type
            self.ui.cb_passType.setCurrentText(self.ui.cb_passType.keys().index('smoothShaded'))
            self.pbMngr.set_pass_type(str(self.ui.cb_passType.currentText()))
            # camera type
            self.ui.cb_cameraType.setCurrentText(self.ui.cb_cameraType.keys().index('perspective'))
            self.pbMngr.set_camera_type(str(self.ui.cb_cameraType.currentText()))

        except:
            self._app.logger.debug("Could not set the ui defaults -_-")

    def gatherUiData(self):
        """
        method to gather ui data.
        :return:
        """
        # change the encoding as per format choice
        # if str(self.ui.cb_format.currentText()) == "image":
        #     # encoding = 'jpeg'
        #     #maya_output = self.pbMngr.get_temp_output(ext='jpeg')
        # else:
        #     # if str(self.ui.cb_format.currentText) == "avi":
        #     #encoding = 'avi'
        #     # encoding = 'H.264'
        #     #maya_output = self.pbMngr.get_temp_output(ext='avi')

        # self._app.logger.debug("(gatherUiData: encoding = {0}, maya_output = {1})".format(
        #                                                                         encoding,
        #                                                                         maya_output))

        playblastParams = {
            'startTime': int(self.ui.frameRange_start.text()),
            'endTime': int(self.ui.frameRange_end.text()),
            'forceOverwrite': True,
            'format': str(self.ui.cb_format.currentText()),
            'percent': float(self.ui.lineEdit_scale.text()) * 100,
            # 'compression': 'H.264',
            'width': int(float(self.ui.lineEdit_finalRes_w.text())),
            'height': int(float(self.ui.lineEdit_finalRes_h.text())),
            'offScreen': True,
            # 'quality': 70,
            # 'viewer': True,
            'framePadding': int(self.ui.lineEdit_framePadding.text()),
            # 'filename': maya_output,
            'filename': self.pbMngr.get_temp_output('.avi')  # self.pbMngr.formatOutputPath(),
            # 'compression': encoding
        }
        self.pbMngr.set_pass_type(str(self.ui.cb_passType.currentText()))
        self.pbMngr.set_description(str(self.ui.textEdit_comment.toPlainText()))
        self.pbMngr.set_camera_type(str(self.ui.cb_cameraType.currentText()))

        self._app.logger.debug("playblastParams gathered: ")
        self._app.logger.debug(playblastParams)

        self._app.logger.debug("cb_passType.currentText= {}".format(str(self.ui.cb_passType.currentText())))
        self._app.logger.debug("textEdit_comment= {}".format(str(self.ui.textEdit_comment.toPlainText())))
        self._app.logger.debug("cb_cameraType.currentText= {}".format(str(self.ui.cb_cameraType.currentText())))

        # self._app.logger.debug("playblastParams['filename'] = {} ".format(playblastParams['filename']))
        pprint.pprint(playblastParams)
        return playblastParams

    def doPlayblast(self):
        """
        method envoked when ui's playblast button is clicked
        :return:
        """
        overridePlayblastParams = {}
        overridePlayblastParams = self.gatherUiData()

        playblastFile = self.pbMngr.createPlayblast(overridePlayblastParams)
        self._app.logger.info("Playblast created = {}".format(playblastFile))

        #self.pbMngr.uploadToShotgun(playblastFile)
