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
import os
import traceback
import subprocess
from functools import partial

import sgtk
from sgtk.platform.qt import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

import maya.cmds as cmds

from .ui.dialog import Ui_Dialog
from .playblast import PlayblastManager

logger = sgtk.platform.get_logger(__name__)
camera_utils = sgtk.platform.import_framework("tvfx-maya-utils", "camera_utils")
shotgun_menus = sgtk.platform.import_framework("tk-framework-qtwidgets", "shotgun_menus")


def show_dialog(app_instance, version_str='0.0.1'):
    """
    Shows the main dialog window, using the special Shotgun multi-select mode.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 
    
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    AppDialog.__version__ = version_str
    app_instance.engine.show_dialog("Maya Playblast - v{}".format(version_str),  # window title
                                    app_instance,                               # playblast instance
                                    AppDialog)


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """

    def __init__(self, parent=None):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent=parent)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Status bar

        # self.ui.statusBar.setObjectName(_fromUtf8("statusbar"))
        # QtGui.QWidget.setStatusBar(self.ui.statusBar)
        # self.setStatusBar(self.statusBar)
        self.ui.status_bar = QtGui.QStatusBar()
        self.ui.status_bar.setSizeGripEnabled(False)
        # hbox_status_bar = QtGui.QHBoxLayout()
        # hbox_status_bar.addStretch(1)
        # hbox_status_bar.addWidget(self.ui.statusBar)
        self.ui.hl_control_layout_3.addWidget(self.ui.status_bar)
        # self.ui.formLayout_3.layout().addLayout(hbox_status_bar)

        # self.ui.status_bar.addPermanentWidget(QtGui.QLabel("message to right end"))
        self.ui.status_bar.showMessage('Ready to playblast', msecs=2000)

        # Progress bar
        # self.ui.progressBar.setValue(0)



        # --- add resolution presets
        self.ui.tb_resolution_preset.hide()
        self.ui.sb_scale.setValue(1.0)

        self.ui.cb_resolution.currentTextChanged.connect(self._toggle_custom_res_type)
        self.ui.cb_pass_type.currentTextChanged.connect(self._toggle_custom_pass_type)
        self.ui.cb_camera_type.currentTextChanged.connect(self._toggle_custom_camera_type)
        # self.ui.pb_cancel.released.connect(self.deleteLater)
        self.ui.le_pass_type_custom.setVisible(False)
        self.ui.le_camera_custom.setVisible(False)

        self.ui.le_frame_start.setValidator(QtGui.QIntValidator(self))
        self.ui.le_frame_end.setValidator(QtGui.QIntValidator(self))

        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk
        self._app = sgtk.platform.current_bundle()
        self.context = None

        # self.pbMngr = PlayblastManager(self._app, self.context, partial(self.set_status, 2000))
        self.pbMngr = PlayblastManager(self._app, self.context, self.set_status)
        self.set_default_ui_data()

        # logging happens via a standard toolkit logger
        self._app.logger.info("Track's maya playblast")

        # lastly, set up our very basic UI
        # self.ui.createPlayblast.clicked.connect(self.ui.progressBar)
        self.ui.createPlayblast.clicked.connect(self.do_playblast)

    def set_status(self, message, msecs=1460, log=True):
        if self.ui.status_bar:
            if log:
                self._app.logger.info(message)
            self.ui.status_bar.showMessage(message, msecs)

        QtGui.QApplication.processEvents()

    def start_progress(self):
        pass

    def show_status(self, title, message):
        self._app.engine.show_busy(title, message)

    def _toggle_custom_res_type(self, val):
        if val == 'From Viewport':
            w, h = self._get_maya_window_resolution()
            self.ui.sb_res_w.setValue(w)
            self.ui.sb_res_h.setValue(h)
        elif val == 'From Render Settings':
            w, h = self._get_maya_render_resolution()
            self.ui.sb_res_w.setValue(w)
            self.ui.sb_res_h.setValue(h)

        if val == 'Custom':
            self.ui.sb_res_w.setEnabled(True)
            self.ui.sb_res_h.setEnabled(True)
        else:
            self.ui.sb_res_w.setEnabled(False)
            self.ui.sb_res_h.setEnabled(False)

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

    def _get_maya_window_resolution(self):
        cmds.currentTime(cmds.currentTime(query=True))
        panel = cmds.playblast(activeEditor=True)
        panel_name = panel.split("|")[-1]
        width = cmds.control(panel_name, query=True, width=True)
        height = cmds.control(panel_name, query=True, height=True)
        return width, height

    def _get_maya_render_resolution(self):
        width = cmds.getAttr('defaultResolution.width')
        height = cmds.getAttr('defaultResolution.height')
        return width, height

    def get_res(self):
        if self.ui.cb_resolution == "From Viewport":
            w, h = self.pbMngr.get_maya_window_resolution()
        elif self.ui.cb_resolution == "From Render Settings":
            w, h = self.pbMngr.get_maya_window_resolution()
        else:
            w = self.ui.sb_res_w.value()
            h = self.ui.sb_res_h.value()

        return w, h

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
            self.ui.sb_scale.setValue(1.0)

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
        camera_type = self.ui.cb_camera_type.currentText()
        if camera_type == "Custom":
            camera_type = self.ui.le_camera_custom.text()

        return camera_type

    @property
    def pass_type(self):
        pass_type = self.ui.cb_pass_type.currentText()
        if pass_type == 'Custom':
            pass_type = self.ui.le_pass_type_custom.text()

        return pass_type

    def gatherUiData(self):
        """
        method to gather ui data.
        :return:
        """
        width, height = self.get_res()

        if str(self.ui.cb_format.currentText()) == "image":
            extension = ".jpg"
            encoding = "jpg"
        elif str(self.ui.cb_format.currentText()) == "avi":
            extension = ".avi"
            encoding = "none"
        else:
            extension = ".avi"
            encoding = "none"

        playblastParams = {
            'startTime': int(self.ui.le_frame_start.text()),
            'endTime': int(self.ui.le_frame_end.text()),
            'forceOverwrite': True,
            'format': str(self.ui.cb_format.currentText()),
            'percent': float(self.ui.sb_scale.value()) * 100,
            # 'compression': 'H.264',
            # 'width': int(float(self.ui.sb_res_w.value())),
            # 'height': int(float(self.ui.sb_res_h.value())),
            'width': width,
            'height': height,

            'offScreen': True,
            # 'quality': 70,
            # 'viewer': True,
            'framePadding': int(self.ui.sb_padding.value()),
            # 'filename': maya_output,
            'filename': self.pbMngr.get_temp_output(extension),  # self.pbMngr.format_output_path(),
            'compression': encoding
        }
        self.pbMngr.set_pass_type(self.pass_type)
        self.pbMngr.set_camera_type(self.camera_type)
        self.pbMngr.set_focal_length(self.ui.sb_focal.value())

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
        # msg = QtGui.QMessageBox()
        # msg.setIcon(QtGui.QMessageBox.Information)
        # msg.setWindowTitle("Playblast app messages")
        # self.show_status('Playblast in progress..', 'Getting playblast out..')
        overridePlayblastParams = self.gatherUiData()

        # self.ui.status_bar.showMessage('User input gathered', msecs=2000)
        self.set_status('User input gathered')
        playblastFile, entity = self.pbMngr.createPlayblast(overridePlayblastParams)


        # self._app.logger.info("Playblast created and uploaded to shotgun = {}".format(playblastFile))
        # self._app.engine.clear_busy()
        # msg.information(self, 'Playblast created', 'A New Version of playblast has been created.')

        # msg.setInformativeText("Playblast created and uploaded to shotgun!")
        # msg.setDetailedText("Playblast path: ".format(playblastFile))

        QtGui.QMessageBox.information(self, 'Playblast created:', 'New Version: {}'.format(playblastFile))
        try:
            bin = 'rv'
            if os.path.exists('/opt/rv/rv-centos7-x86-64-7.6.1/bin/rv'):
                bin = '/opt/rv/rv-centos7-x86-64-7.6.1/bin/rv'
            subprocess.Popen([bin, '-play', playblastFile])
        except:
            pass

        url = 'https://trackvfx.shotgunstudio.com/detail/{}/{}'.format(entity['type'], entity['id'])
        if os.name == 'posix':
            subprocess.Popen(['xdg-open', url], close_fds=True)
        elif os.name == 'nt':
            os.startfile(url)


