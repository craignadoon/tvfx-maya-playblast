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
import glob

import os
import sys
import tabulate
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
    _app = sgtk.platform.current_bundle()
    if not _app.context.entity:
        QtGui.QMessageBox.warning(None, 'Task Context not Found!!',  'Open/Save file from SG!!!!!!!!!!!!')
        return
    AppDialog.__version__ = version_str
    app_instance.engine.show_dialog("Maya Playblast - v{}".format(version_str),  # window title
                                    app_instance,  # playblast instance
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

        self.ui.status_bar = QtGui.QStatusBar()
        self.ui.status_bar.setSizeGripEnabled(False)
        self.ui.hl_control_layout_3.addWidget(self.ui.status_bar)
        self.ui.status_bar.showMessage('Ready to playblast', msecs=2000)

        # --- add resolution presets
        self.ui.tb_resolution_preset.hide()
        self.ui.sb_scale.setValue(1.0)

        self.ui.cb_resolution.currentTextChanged.connect(self._toggle_custom_res_type)
        # self.ui.sb_res_w.valueChanged.connect(self.resolution_width_changed)
        self.ui.cb_pass_type.currentTextChanged.connect(self._toggle_custom_pass_type)
        self.ui.cb_camera_type.currentTextChanged.connect(self._toggle_custom_camera_type)
        self.ui.le_pass_type_custom.setVisible(False)
        self.ui.le_camera_custom.setVisible(False)

        self.ui.le_frame_start.setValidator(QtGui.QIntValidator(self))
        self.ui.le_frame_end.setValidator(QtGui.QIntValidator(self))

        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk
        self._app = sgtk.platform.current_bundle()

        # if not self._app.context.entity:
        #     QtGui.QMessageBox.warning(self, 'Task Context not Found!!',
        #                               'Kindly open file from Shotgrid menu!!!!!!!!!!!!')
        #     self.destroy_app()
            # return
            # self.close()
        self.context = None

        # self.pbMngr = PlayblastManager(self._app, self.context, partial(self.set_status, 2000))
        # self.pbMngr = PlayblastManager(self._app, self.context, self.set_status)
        self.pbMngr = PlayblastManager(self._app, self.context)
        self.is_anamorphic = False
        self.set_default_ui_data()

        # logging happens via a standard toolkit logger
        self._app.logger.info("Track's maya playblast")

        # lastly, set up our very basic UI
        self.ui.createPlayblast.clicked.connect(self.do_playblast)
        self.ui.pb_cancel.clicked.connect(self._on_cancel)
        self.ui.pb_refresh.clicked.connect(self._on_pb_refresh)
        self.ui.sb_scale.valueChanged.connect(self._on_sb_change)
        self.ui.cb_auto.stateChanged.connect(self._on_cb_auto_change)
        self.ui.cb_anamorphic.stateChanged.connect(self._on_cb_anamorphic_change)
        self.ui.createPlayblast.setFocus()
        self.resize(500, 250)
        self._on_cb_auto_change()
        self._on_sb_change()

    def _on_cb_anamorphic_change(self):
        print("self.ui.cb_anamorphic.isChecked()", self.ui.cb_anamorphic.isChecked())
        if self.ui.cb_anamorphic.isChecked():
            self.is_anamorphic = True
        else:
            self.is_anamorphic = False

        val = str(self.ui.cb_resolution.currentText())
        if val == 'From Render Settings':
            w, h = self._get_maya_render_resolution()
            if self.is_anamorphic:
                aspect_ratio = float(w) / float(h)
                print(aspect_ratio)
                h = float(h / aspect_ratio)
            self.ui.sb_res_w.setValue(w)
            self.ui.sb_res_h.setValue(h)
            self._on_cb_auto_change()
            print(w, h)

    def _on_cb_auto_change(self):
        if self.ui.cb_auto.isChecked():
            width_value = int(self.ui.sb_res_w.value())
            scale_value = float(2048.0 / width_value)
            if scale_value != round(scale_value, 2):
                scale_value = scale_value - 0.01
            self.ui.sb_scale.setValue(scale_value)
            self.ui.sb_scale.setEnabled(0)
        else:
            self.ui.sb_scale.setEnabled(1)

    def _on_sb_change(self):
        width_value = int(self.ui.sb_res_w.value())
        actual_width = float(self.ui.sb_scale.value()) * width_value
        if 2048 < actual_width:
            self.ui.lbl_resolution_size_hint.show()
            self.ui.lbl_resolution_size_hint.setStyleSheet("color: red")
        else:
            self.ui.lbl_resolution_size_hint.hide()

    def _on_pb_refresh(self):
        val = str(self.ui.cb_resolution.currentText())
        if val == 'From Render Settings':
            w, h = self._get_maya_render_resolution()
            if self.is_anamorphic:
                aspect_ratio = float(w) / float(h)
                h = float(h / aspect_ratio)
            self.ui.sb_res_w.setValue(w)
            self.ui.sb_res_h.setValue(h)
            self._on_cb_auto_change()

    def _on_cancel(self):
        """
        Called when the cancel button is clicked
        """
        self._exit_code = QtGui.QDialog.Rejected
        self.close()

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

    def resolution_width_changed(self):
        width_value = int(self.ui.sb_res_w.value())
        if 2048 < width_value:
            self.ui.lbl_resolution_size_hint.show()
            self.ui.lbl_resolution_size_hint.setStyleSheet("color: red")
        else:
            self.ui.lbl_resolution_size_hint.hide()

    def _toggle_custom_res_type(self, val):
        if val == 'From Viewport':
            w, h = self._get_maya_window_resolution()
            if self.is_anamorphic:
                aspect_ratio = float(w) / float(h)
                h = float(h / aspect_ratio)
            self.ui.sb_res_w.setValue(w)
            self.ui.sb_res_h.setValue(h)
            self.ui.pb_refresh.hide()
            self.ui.cb_auto.hide()
        elif val == 'From Render Settings':
            w, h = self._get_maya_render_resolution()
            if self.is_anamorphic:
                aspect_ratio = float(w) / float(h)
                h = float(h / aspect_ratio)
            self.ui.sb_res_w.setValue(w)
            self.ui.sb_res_h.setValue(h)
            self.ui.pb_refresh.show()
            self.ui.cb_auto.show()
        if val == 'Custom':
            self.ui.sb_res_w.setEnabled(True)
            self.ui.sb_res_h.setEnabled(True)
            self.ui.pb_refresh.hide()
            self.ui.cb_auto.hide()
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
        # auto_crop = True if self.ui.cb_auto.isChecked() else False
        # if 2048 < int(w) and auto_crop:
        #     w, h = self.pbMngr.get_resolution(w, h)
        return w, h

    def set_default_ui_data(self):
        """
        method to set defaults in ui to minimize user input.
        :return:
        """
        try:
            # FRAME RANGE: from maya scene
            start_frame, end_frame, self.is_anamorphic = self.pbMngr.get_frame_range()
            if self.is_anamorphic:
                self.ui.cb_anamorphic.setChecked(True)
            self._app.logger.info("set_default_ui_data: start_frame, end_frame = {0}, {1}".format(start_frame,
                                                                                                  end_frame))
            self.ui.le_frame_start.setText(str(start_frame))

            self.ui.le_frame_end.setText(str(end_frame))

            # getting default values for yaml file
            camera_type_value, pass_type, frame_padding, scale = self.pbMngr.get_defaults_values()

            # SCALE:
            self.ui.sb_scale.setValue(scale)
            self.hide_elements()

            # FRAME PADDING: how many frames before the start frame
            self.ui.sb_padding.setValue(frame_padding)
            # self.ui.sb_padding.setVisible(False)

            self.ui.le_focal_length.setText(self.pbMngr.get_focal_length_min_max())
            self.ui.le_focal_length.setEnabled(False)

            # RESOLUTION : (hard coding for now)
            self.ui.sb_res_w.setValue(960)
            self.ui.sb_res_h.setValue(540)

            # FORMAT: default playblast format is set to movie as of now
            self.ui.cb_format.setCurrentIndex(0)

            # pass type
            self.ui.cb_pass_type.setCurrentText(pass_type)
            self.pbMngr.set_pass_type(str(self.ui.cb_pass_type.currentText()).lower())

            # camera type
            self.ui.cb_camera_type.setCurrentText(camera_type_value)
            self.pbMngr.set_camera_type(str(self.ui.cb_camera_type.currentText()))

            # description
            context = self.pbMngr.get_context()

            # adding to resolutions
            self.ui.cb_resolution.setCurrentText("From Render Settings")
            # self.resolution_width_changed()

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

        return str(pass_type).lower()

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
            'width': width,
            'height': height,

            'offScreen': True if self.ui.checkBox.isChecked() else False,
            'framePadding': int(self.ui.sb_padding.value()),
            'filename': self.pbMngr.get_temp_output(extension),  # self.pbMngr.fofrmat_output_path(),
            'compression': encoding
        }
        self.pbMngr.set_pass_type(self.pass_type)
        self.pbMngr.set_camera_type(self.camera_type)
        self.pbMngr.set_focal_length(self.ui.le_focal_length.text())

        # description = 'FocalLength: {},\n PassType: {},\n CameraType: {},\n Comments: {}\n'.format(
        #     self.ui.le_focal_length.text(), self.pass_type, self.camera_type, self.ui.le_comments.text()
        # )

        description = 'Playblast Data:\n\n{}'.format(tabulate.tabulate(
            [
                ("FocalLength", str(self.ui.le_focal_length.text())),
                ("PassType", str(self.pass_type)),
                ("CameraType", str(self.camera_type)),
                ("Comments", str(self.ui.le_comments.text())),
                ("Percent", float(self.ui.sb_scale.value()) * 100)

            ],
            headers=['Data', 'Value'], tablefmt='pipe', colalign=('right', 'left')))
        self.pbMngr.set_description(description)
        self.pbMngr.upload_to_sg = True if self.ui.cb_upload_sg.isChecked() else False

        self._app.logger.debug("playblastParams gathered: ")
        self._app.logger.debug(playblastParams)

        self._app.logger.debug("cb_passType.currentText= {}".format(str(self.ui.cb_pass_type.currentText())))
        self._app.logger.debug("plainTextEdit_comment= {}".format(str(self.ui.le_comments.text())))
        self._app.logger.debug("cb_cameraType.currentText= {}".format(str(self.ui.cb_camera_type.currentText())))

        # self._app.logger.debug("playblastParams['filename'] = {} ".format(playblastParams['filename']))
        logger.info(playblastParams)
        return playblastParams

    def get_rv_path(self):
        if os.name == 'nt':
            paths = glob.glob(r'C:\Program Files\Shotgun\*\bin\rv.exe')
        else:
            paths = glob.glob('/opt/rv/*/bin/rv')

        if paths:
            paths.sort()
            return paths[0]

        return 'rv'

    def do_playblast(self):
        """
        method invoked when ui's playblast button is clicked
        :return:
        """
        if self.ui.le_comments.text() == "":
            QtGui.QMessageBox.warning(self, 'comments error', 'Comment should be mandatory')
            return

        overridePlayblastParams = self.gatherUiData()

        # self.ui.status_bar.showMessage('User input gathered', msecs=2000)
        self.set_status('Play blast in process')
        playblastFile, entity = self.pbMngr.createPlayblast(overridePlayblastParams)
        self.set_status('')
        QtGui.QMessageBox.information(self, 'Playblast created:',
                                      'New Version: {}'.format(os.path.basename(playblastFile)))
        try:
            bin = self.get_rv_path()
            subprocess.Popen([bin, '-play', playblastFile])
        except:
            pass

        if entity:
            url = 'https://trackvfx.shotgunstudio.com/detail/{}/{}'.format(entity['type'], entity['id'])
            if os.name == 'posix':
                subprocess.Popen(['xdg-open', url], close_fds=True)
            elif os.name == 'nt':
                os.startfile(url)

    def hide_elements(self, value=False):
        self.ui.le_frame_start.setVisible(value)
        self.ui.le_frame_end.setVisible(value)
        self.ui.label_3.setVisible(value)
        self.ui.label_1_frameRange.setVisible(value)
        self.ui.label_format.setVisible(value)
        self.ui.label_framePadding.setVisible(value)
        self.ui.sb_padding.setVisible(value)
        self.ui.cb_format.setVisible(value)
