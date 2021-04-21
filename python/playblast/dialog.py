# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
import sgtk
import traceback
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog
from .playblast import PlayblastManager

logger = sgtk.platform.get_logger(__name__)
camera_utils = sgtk.platform.import_framework("tvfx-maya-utils", "camera_utils")


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

        self.ui.cb_pass_type.currentTextChanged.connect(self._toggle_custom_pass_type)
        self.ui.cb_camera_type.currentTextChanged.connect(self._toggle_custom_camera_type)
        self.ui.pb_cancel.released.connect(self.deleteLater)
        self.ui.le_pass_type_custom.setVisible(False)
        self.ui.le_camera_custom.setVisible(False)

        self.ui.le_frame_start.setValidator(QtGui.QIntValidator(self))
        self.ui.le_frame_end.setValidator(QtGui.QIntValidator(self))

        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()
        self._app.logger.debug("$$$$ self._app = {}".format(self._app))
        self.context = None

        self.pbMngr = PlayblastManager(self._app,self.context)
        self.set_default_ui_data()
        self._app.logger.info("$$$$ set_default_ui_data DONE ")

        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk 

        # logging happens via a standard toolkit logger
        self._app.logger.info("Track's maya playblast")

        # lastly, set up our very basic UI
        # self.ui.context.setText("Current selection type: %s, <br>Currently selected ids: %s" % (entity_type, entity_ids))
        self.ui.createPlayblast.clicked.connect(self.do_playblast)

    def _toggle_custom_pass_type(self, val):
        if val == 'Custom':
            self.ui.le_pass_type_custom.setVisible(True)
        else:
            self.ui.le_pass_type_custom.setVisible(False)

    def _toggle_custom_camera_type(self, val):
        if val == 'Custom':
            self.ui.le_camera_custom.setVisible(True)
        else:
            self.ui.le_camera_custom.setVisible(False)

    def set_default_ui_data(self):
        """
        method to set defaults in ui to minimize user input.
        :return:
        """
        try:
            # FRAME RANGE: from maya scene
            start_frame, end_frame = self.pbMngr.get_frame_range()
            self._app.logger.info("set_default_ui_data: start_frame, end_frame = {0}, {1}".format(start_frame,
                                                                                                  end_frame))
            self.ui.le_frame_start.setText(str(start_frame))
            self.ui.le_frame_end.setText(str(end_frame))

            # SCALE:
            self.ui.sb_scale.setValue(0.5)

            # FRAME PADDING: how many frames before the start frame
            self.ui.sb_padding.setValue(4)
            self.ui.sb_focal.setValue(35)

            # RESOLUTION : (hard coding for now)
            self.ui.sb_res_w.setValue(960)
            self.ui.sb_res_h.setValue(540)

            # FORMAT: default playblast format is set to movie as of now
            self.ui.cb_format.setCurrentIndex(0)

            # pass type
            self.ui.cb_pass_type.setCurrentIndex(0)
            self.pbMngr.set_pass_type(str(self.ui.cb_pass_type.currentText()))

            # camera type
            self.ui.cb_camera_type.setCurrentIndex(0)
            self.pbMngr.set_camera_type(str(self.ui.cb_camera_type.currentText()))

            # description
            context = self.pbMngr.get_context()
            self._app.logger.debug(
                "set_default_ui_data: playblast for {0}, {1}".format(context.entity, context.project))

        except Exception as err:
            print(traceback.format_exc())
            self._app.logger.debug("Could not set the ui defaults: {}".format(err))

    @property
    def camera_type(self):
        camera_type = self.cb_camera_type.currentText()
        if camera_type == "Custom":
            camera_type = self.le_camera_custom.text()

        return camera_type

    @property
    def pass_type(self):
        pass_type = self.cb_pass_type.currentText()
        if pass_type == 'Custom':
            pass_type = self.le_pass_type_custom.text()

        return pass_type

    def gatherUiData(self):
        """
        method to gather ui data.
        :return:
        """
        playblastParams = {
            'startTime': int(self.ui.le_frame_start.text()),
            'endTime': int(self.ui.le_frame_end.text()),
            'forceOverwrite': True,
            'format': str(self.ui.cb_format.currentText()),
            'percent': float(self.ui.sb_scale.value()) * 100,
            # 'compression': 'H.264',
            'width': int(float(self.ui.sb_res_w.value())),
            'height': int(float(self.ui.sb_res_h.value())),
            'offScreen': True,
            # 'quality': 70,
            # 'viewer': True,
            'framePadding': int(self.ui.sb_padding.value()),
            # 'filename': maya_output,
            'filename': self.pbMngr.get_temp_output('.avi')  # self.pbMngr.format_output_path(),
            # 'compression': encoding
        }
        self.pbMngr.set_pass_type(self.pass_type)
        self.pbMngr.set_camera_type(self.camera_type)
        description = 'FocalLength: {}mm, PassType: {}, CameraType: {}, Comments: {}'.format(
            self.ui.sb_focal.value(), self.pass_type, self.camera_type, self.ui.le_comments.text()
        )
        self.pbMngr.set_description(description)

        self._app.logger.debug("playblastParams gathered: ")
        self._app.logger.debug(playblastParams)

        self._app.logger.debug("cb_passType.currentText= {}".format(str(self.ui.cb_pass_type.currentText())))
        self._app.logger.debug("plainTextEdit_comment= {}".format(str(self.ui.le_comments.text())))
        self._app.logger.debug("cb_cameraType.currentText= {}".format(str(self.ui.cb_camera_type.currentText())))

        # self._app.logger.debug("playblastParams['filename'] = {} ".format(playblastParams['filename']))
        logger.info(playblastParams)
        return playblastParams

    def do_playblast(self):
        """
        method invoked when ui's playblast button is clicked
        :return:
        """
        overridePlayblastParams = {}
        overridePlayblastParams = self.gatherUiData()

        playblastFile = self.pbMngr.createPlayblast(overridePlayblastParams)
        self._app.logger.info("Playblast created and uploaded to shotgun = {}".format(playblastFile))
