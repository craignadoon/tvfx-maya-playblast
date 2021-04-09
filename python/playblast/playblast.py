# coding=utf-8
import pprint
import os
import re

import maya.cmds as cmds
import sgtk

try:
    from sgtk.platform.qt import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui


class PlayblastManager(object):
    __uploadToShotgun = True

    """
    Main playblast functionality
    """
    def __init__(self, app, context=None):
        """
        Construction
        """
        self._app = app
        self._context = context if context else self._app.context

        self._currentEngine = sgtk.platform.current_engine()
        self._tk = self._currentEngine.sgtk

        # self._context = currentEngine.context
        if self._context is None:
            self._context = self._currentEngine.context
                # self.getContext()

        self._app.logger.info("Playblast self._context = {}".format(self._context))

        self.playblastPath = None
        self.playblastParams = {
                            'filename': "C:/work/tempPlayblast/mayaplayblast.mov",
                            'offScreen': True,
                            'percent': 50,
                            'quality': 70,
                            'viewer': True,
                            'width': 960,
                            'height': 540,
                            'framePadding': 4,
                            'format': 'avi',
                            # 'encoding': 'jpg',
                            'compression': 'H.264',
                            'forceOverwrite': True,
                            }

    def getContext(self):
        # currentEngine = sgtk.platform.current_engine()
        # self._app.logger.debug("currentEngine.context.entity = {}".format(currentEngine.context.entity))
        # self._app.logger.debug("currentEngine.context.step = {}".format(currentEngine.context.step))
        # self._app.logger.debug("currentEngine.context.task = {}".format(currentEngine.context.task))
        # self._tk = currentEngine.sgtk
        # self._context = currentEngine.context
        # return currentEngine.context, currentEngine.sgtk, currentEngine
        self._app.logger.debug("self._context.entity = {}".format(self._context.entity))
        self._app.logger.debug("self._context.step = {}".format(self._context.step))
        self._app.logger.debug("self._context.task = {}".format(self._context.task))
        return self._context

        #taskPath = r'X:\Projects\test_test\sequences\rd\FTWD_0611_035_0020\track\work\maya\FTWD_0611_035_0020_track_weirdBall_v001.npawar.ma'
        #tk = sgtk.sgtk_from_path(taskPath)
        #tk = currentEngine.sgtk

        # self._app.logger.debug("tk = {}".format(tk))
        #     self._app = sgtk.platform.current_bundle()
        #     self._current_engine = sgtk.platform.current_engine()
        #     self._context = self._current_engine.context
        #     self._shotgun = self._current_engine.shotgun
        #     self._toolkit = self._current_engine.sgtk

    def getFrameRange(self):
        """
        function to get frame range from current maya scene
        :returns:
            start (int): start frame
            end (int): end frame
        """
        start = int(cmds.playbackOptions(q=True, minTime=True))
        end = int(cmds.playbackOptions(q=True, maxTime=True))
        self._app.logger.debug("getfFrameRange(): start, end frame = {0}, {1}".format(start, end))

        return start, end

        # return int(cmds.playbackOptions(q=True, minTime=True)), \
        #        int(cmds.playbackOptions(q=True, maxTime=True))

    def createPlayblast(self, overridePlayblastParams):
        """
        function to call maya's internal playblast command to create playblast
        as per user input in ui.
        :param
            overridePlayblastParams (dict): user input from ui
        :return:
            playblastPath: output playblast file path.
        """
        filename = "C:/work/tempPlayblast/mayaplayblast.mov"
        self.playblastParams.update(overridePlayblastParams)
        # TODO: filename
        self._app.logger.debug("&&&&& self.playblastParams():")
        self._app.logger.debug(self.playblastParams)
        # if not self.focus:
        #     self.focus = True
        print "in playblast.py before creating playblast"
        # self.playblastPath = self.formatOutputPath()
        self.playblastPath = cmds.playblast(**self.playblastParams)
        self._app.logger.debug("playblastPath = {}".format(self.playblastPath))
        print "playblastPath = {}".format(self.playblastPath)
        print "in playblast.py before return"
        return self.playblastPath

    def formatOutputPath(self):
        """
        function to format output file path as per template.
            maya_playblast_publish_image
            maya_playblast_publish_mov
        in templates.yml in config
        :return:
             publishPath: formatted output file path
        """
        # "@shot_export_area/{plate_name}/{Step}/{publish_type}/v{version}/@resolution/{ext}" \
        # "/{Shot}_{Step}_{pass_type}_[{name}_]v{version}[.{framecount}f].{ext}"
        # maya_playblast_publish_image
        #
        # maya_playblast_publish_mov
        # TODO: condn to check if its a shot context or not
        # TODO: warning if its not a shot context?
        # context = self.getContextInfo()
        try:
            self._tk.create_filesystem_structure("Task", self._context.task["id"])
            self._app.logger.debug("create_filesystem_structure done")
        except:
            print(Exception)
            self._app.logger.debug("create_filesystem_structure failed")

        if self.playblastParams[format] == "image":
            template = self._tk.templates["maya_playblast_publish_image"]
        else:
            template = self._tk.templates["maya_playblast_publish_mov"]

        # template = self._tk.templates["maya_shot_publish"]
        # pprint.pprint("template = ", template)
        fields = self._context.as_template_fields(template)
        pprint.pprint(fields)
        self._app.logger.debug("fields: {}".format(fields))
        # from the input: ['publish_type', 'plate_name',
        # 'ext', 'height', 'width', 'version', 'pass_type']

        # publish_type = ['Geometry', 'Locator', 'Camera', 'Lense', '2DTracks']
        if self.playblastParams[format] == "image":
            fields["publish_type"] = "image"
            fields["ext"] = "jpg"
        else:
            fields["publish_type"] = "movie"
            fields["ext"] = "avi"
        fields["plate_name"] = self.getPlateName()
        fields["height"] = int(self.playblastParams['height'])
        fields["width"] = int(self.playblastParams['width'])
        fields["version"] = 001
        # TODO: pass_type: based on what?
        fields["pass_type"] = 'pass_type'
        print ("field values assigned")

        publishPath = template.apply_fields(fields)
        self._app.logger.debug("publishPath: {}".format(publishPath))
        self._currentEngine.ensure_folder_exists(os.path.dirname(publishPath))


        sgtk.util.filesystem.touch_file(publishPath)
        return publishPath

    def get_plate_name_from_entity(self, entity):
        """Parses plate's PublishedFile entity and returns plate name
        Args:
            entity(dict): PublishedFile entity of type plate
        Returns:
            str: plate name
        """
        pattern = re.compile(('\S+\w+'))

        description = entity.get('description') or ''
        description = description.split('\n')[-1]
        details = pattern.findall(description)
        if details:
            return details[1]
        return ''

    def getPlateName(self):
        """Returns plate names associated with the context
            Args:
                context: sgtk.Context, *Optional* if not provided
                    uses current entity
            Returns:
                str: plate name parsed from PublishedFile of type Image
        """
        pass_name = 'Main'
        # plates = get_plate_entity(context)
        plates = self._context.sgtk.shotgun.find(
                    'PublishedFile',
                    [
                        ['entity', 'is', self._context.entity],
                        ['sg_pass_type', 'is', pass_name]
                    ],
                    ['sg_client_name', 'description'],
                    order=[{'field_name': 'sg_version_number', 'direction': 'desc'}]
                ) or []

        plate_names = list()
        for plate in plates:
            plate_names.append(self.get_plate_name_from_entity(plate))
        return plate_names[0]

    def uploadToShotgun(self):
        """
        To upload the playblast img seq/mov to shotgun
        :return:
        """
        # register new Version entity in shotgun or update existing version, minimize shotgun data
        playblastMovie = self.playblastPath
        project = self._app.context.project
        entity = self._app.context.entity
        task = self._app.context.task

        # todo: version update and use publishPath (check fields first)
        self._app.log_info("Playblast finished")

