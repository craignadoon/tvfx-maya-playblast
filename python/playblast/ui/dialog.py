# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\work\TrackVFX\tk\tvfx-maya-playblast\resources\dialog.ui'
#
# Created: Tue Apr 20 20:34:38 2021
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

#from PySide import QtCore, QtGui
try:
    from sgtk.platform.qt import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(574, 302)
        self.gridLayout_4 = QtGui.QGridLayout(Dialog)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.logo_example = QtGui.QLabel(Dialog)
        self.logo_example.setText("")
        self.logo_example.setPixmap(QtGui.QPixmap(":/res/sg_logo.png"))
        self.logo_example.setObjectName("logo_example")
        self.gridLayout_4.addWidget(self.logo_example, 0, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_1_frameRange = QtGui.QLabel(self.groupBox_3)
        self.label_1_frameRange.setObjectName("label_1_frameRange")
        self.gridLayout_3.addWidget(self.label_1_frameRange, 1, 0, 1, 1)
        self.frameRange_end = QtGui.QLineEdit(self.groupBox_3)
        self.frameRange_end.setText("")
        self.frameRange_end.setObjectName("frameRange_end")
        self.gridLayout_3.addWidget(self.frameRange_end, 1, 2, 1, 1)
        self.frameRange_start = QtGui.QLineEdit(self.groupBox_3)
        self.frameRange_start.setText("")
        self.frameRange_start.setObjectName("frameRange_start")
        self.gridLayout_3.addWidget(self.frameRange_start, 1, 1, 1, 1)
        self.lineEdit_finalRes_h = QtGui.QLineEdit(self.groupBox_3)
        self.lineEdit_finalRes_h.setObjectName("lineEdit_finalRes_h")
        self.gridLayout_3.addWidget(self.lineEdit_finalRes_h, 0, 2, 1, 1)
        self.finalRes_label = QtGui.QLabel(self.groupBox_3)
        self.finalRes_label.setObjectName("finalRes_label")
        self.gridLayout_3.addWidget(self.finalRes_label, 0, 0, 1, 1)
        self.lineEdit_finalRes_w = QtGui.QLineEdit(self.groupBox_3)
        self.lineEdit_finalRes_w.setObjectName("lineEdit_finalRes_w")
        self.gridLayout_3.addWidget(self.lineEdit_finalRes_w, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_3, 0, 1, 1, 3)
        self.checkBox = QtGui.QCheckBox(Dialog)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_4.addWidget(self.checkBox, 0, 4, 1, 1)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_scale = QtGui.QLabel(self.groupBox)
        self.label_scale.setObjectName("label_scale")
        self.gridLayout.addWidget(self.label_scale, 0, 0, 1, 1)
        self.lineEdit_scale = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_scale.setText("")
        self.lineEdit_scale.setObjectName("lineEdit_scale")
        self.gridLayout.addWidget(self.lineEdit_scale, 0, 2, 1, 1)
        self.label_format = QtGui.QLabel(self.groupBox)
        self.label_format.setObjectName("label_format")
        self.gridLayout.addWidget(self.label_format, 1, 0, 1, 1)
        self.cb_format = QtGui.QComboBox(self.groupBox)
        self.cb_format.setObjectName("cb_format")
        self.cb_format.addItem("")
        self.cb_format.addItem("")
        self.gridLayout.addWidget(self.cb_format, 1, 2, 1, 1)
        self.label_framePadding = QtGui.QLabel(self.groupBox)
        self.label_framePadding.setObjectName("label_framePadding")
        self.gridLayout.addWidget(self.label_framePadding, 2, 0, 1, 1)
        self.lineEdit_framePadding = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_framePadding.setText("")
        self.lineEdit_framePadding.setObjectName("lineEdit_framePadding")
        self.gridLayout.addWidget(self.lineEdit_framePadding, 2, 2, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 1, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 1, 2, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_6_focalLength = QtGui.QLabel(self.groupBox_2)
        self.label_6_focalLength.setObjectName("label_6_focalLength")
        self.gridLayout_2.addWidget(self.label_6_focalLength, 0, 0, 1, 1)
        self.label_5_cameraType = QtGui.QLabel(self.groupBox_2)
        self.label_5_cameraType.setObjectName("label_5_cameraType")
        self.gridLayout_2.addWidget(self.label_5_cameraType, 1, 0, 1, 1)
        self.cb_cameraType = QtGui.QComboBox(self.groupBox_2)
        self.cb_cameraType.setObjectName("cb_cameraType")
        self.cb_cameraType.addItem("")
        self.cb_cameraType.addItem("")
        self.cb_cameraType.addItem("")
        self.cb_cameraType.addItem("")
        self.cb_cameraType.addItem("")
        self.gridLayout_2.addWidget(self.cb_cameraType, 1, 1, 1, 1)
        self.label_4_passType = QtGui.QLabel(self.groupBox_2)
        self.label_4_passType.setObjectName("label_4_passType")
        self.gridLayout_2.addWidget(self.label_4_passType, 2, 0, 1, 1)
        self.cb_passType = QtGui.QComboBox(self.groupBox_2)
        self.cb_passType.setObjectName("cb_passType")
        self.cb_passType.addItem("")
        self.cb_passType.addItem("")
        self.cb_passType.addItem("")
        self.cb_passType.addItem("")
        self.cb_passType.addItem("")
        self.gridLayout_2.addWidget(self.cb_passType, 2, 1, 1, 1)
        self.lineEdit_focalLength = QtGui.QLineEdit(self.groupBox_2)
        self.lineEdit_focalLength.setObjectName("lineEdit_focalLength")
        self.gridLayout_2.addWidget(self.lineEdit_focalLength, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 1, 3, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 1, 5, 1, 1)
        self.label_comment = QtGui.QLabel(Dialog)
        self.label_comment.setObjectName("label_comment")
        self.gridLayout_4.addWidget(self.label_comment, 2, 0, 1, 1)
        self.plainTextEdit_comment = QtGui.QPlainTextEdit(Dialog)
        self.plainTextEdit_comment.setObjectName("plainTextEdit_comment")
        self.gridLayout_4.addWidget(self.plainTextEdit_comment, 2, 1, 2, 1)
        self.createPlayblast = QtGui.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.createPlayblast.setFont(font)
        self.createPlayblast.setObjectName("createPlayblast")
        self.gridLayout_4.addWidget(self.createPlayblast, 3, 4, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem2, 2, 4, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "The Current Sgtk Environment", None, QtGui.QApplication.UnicodeUTF8))
        self.label_1_frameRange.setText(QtGui.QApplication.translate("Dialog", "Frame Range", None, QtGui.QApplication.UnicodeUTF8))
        self.finalRes_label.setText(QtGui.QApplication.translate("Dialog", "Resolution", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Dialog", "Off Screen", None, QtGui.QApplication.UnicodeUTF8))
        self.label_scale.setText(QtGui.QApplication.translate("Dialog", "Scale", None, QtGui.QApplication.UnicodeUTF8))
        self.label_format.setText(QtGui.QApplication.translate("Dialog", "Format", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_format.setItemText(0, QtGui.QApplication.translate("Dialog", "avi", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_format.setItemText(1, QtGui.QApplication.translate("Dialog", "image", None, QtGui.QApplication.UnicodeUTF8))
        self.label_framePadding.setText(QtGui.QApplication.translate("Dialog", "FramePadding", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6_focalLength.setText(QtGui.QApplication.translate("Dialog", "Focal length", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5_cameraType.setText(QtGui.QApplication.translate("Dialog", "Camera Type", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_cameraType.setItemText(0, QtGui.QApplication.translate("Dialog", "perspective", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_cameraType.setItemText(1, QtGui.QApplication.translate("Dialog", "top", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_cameraType.setItemText(2, QtGui.QApplication.translate("Dialog", "front", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_cameraType.setItemText(3, QtGui.QApplication.translate("Dialog", "bottom", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_cameraType.setItemText(4, QtGui.QApplication.translate("Dialog", "custom", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4_passType.setText(QtGui.QApplication.translate("Dialog", "Pass Type", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_passType.setItemText(0, QtGui.QApplication.translate("Dialog", "smoothShaded", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_passType.setItemText(1, QtGui.QApplication.translate("Dialog", "wireframe", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_passType.setItemText(2, QtGui.QApplication.translate("Dialog", "flatShaded", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_passType.setItemText(3, QtGui.QApplication.translate("Dialog", "boundingBox", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_passType.setItemText(4, QtGui.QApplication.translate("Dialog", "points", None, QtGui.QApplication.UnicodeUTF8))
        self.label_comment.setText(QtGui.QApplication.translate("Dialog", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.createPlayblast.setText(QtGui.QApplication.translate("Dialog", "Playblast!", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
