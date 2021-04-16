# coding=utf-8

import pprint
import shutil
import tempfile

import os
import re

import maya.cmds as cmds
import sgtk

import tank
from tank import path_cache
from sgtk.util import filesystem, LocalFileStorageManager

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
        self.parent = None
        self._app = app
        self._context = context if context else self._app.context

        self._currentEngine = sgtk.platform.current_engine()
        self._tk = self._currentEngine.sgtk

        # self._context = currentEngine.context
        if self._context is None:
            self._context = self._currentEngine.context
                # self.getContext()

        self._app.logger.info("Playblast self._context = {}".format(self._context))

        self.publish_type = "Playblast"
        # self.mayaOutputPath = self.get_temp_output()
        self.mayaOutputPath = None
        self.playblastPath = None
        self.playblastParams = {
                            'offScreen': True,
                            'percent': 50,
                            'quality': 70,
                            'viewer': True,
                            'width': 960,
                            'height': 540,
                            'framePadding': 4,
                            'format': 'avi',
                            # 'encoding': 'jpg',
                            # 'compression': 'None',
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

        # self._app.logger.debug("tk = {}".format(tk))
        #     self._app = sgtk.platform.current_bundle()
        #     self._current_engine = sgtk.platform.current_engine()
        #     self._context = self._current_engine.context
        #     self._shotgun = self._current_engine.shotgun
        #     self._toolkit = self._current_engine.sgtk

    def get_temp_output(self, ext):

        self.mayaOutputPath = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        if self.mayaOutputPath.name:
            self._app.logger.debug("get_temp_output:closing temp file")
            # self.mayaOutputPath.close()
            pb_path_formatted = str(os.path.dirname(self.mayaOutputPath.name).title()
                                    + "\\"
                                    + os.path.basename(self.mayaOutputPath.name))
            self.mayaOutputPath.name = pb_path_formatted
            return pb_path_formatted
            # return self.mayaOutputPath.name
        ver = 0

        # temp_dir = 'C:\\work\\tempPlayblast\\'
        # temp_playblast = "{0}_{1}_playblast_v{2}.{3}".format(
        #                         self._context.entity['name'],
        #                         self._context.step['name'],
        #                         ('%03d' % ver),
        #                         ext)

        self._app.logger.debug("get_temp_output: maya temp output file = {}".format(self.mayaOutputPath))

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

    def createPlayblast(self, overridePlayblastParams):
        """
        function to call maya's internal playblast command to create playblast
        as per user input in ui.gatherUiData
        :param
            overridePlayblastParams (dict): user input from ui
        :return:
            playblastPath: output playblast file path.
        """
        self.playblastParams.update(overridePlayblastParams)
        # TODO: filename
        self._app.logger.debug("&&&&& self.playblastParams():")
        self._app.logger.debug(self.playblastParams)
        # if not self.focus:
        #     self.focus = True
        print "in playblast.py before creating playblast"

        # self.playblastPath = cmds.playblast(**self.playblastParams)
        # self.mayaOutputPath.close()

        # cmds.file(self.mayaOutputPath.name, open=True, force=True)

        self.mayaOutputPath = cmds.playblast(**self.playblastParams)
        self._app.logger.debug("createPlayblast: mayaOutputPath = {}".format(self.mayaOutputPath))

        # outputpath, ext = os.path.splitext(self.mayaOutputPath)
        # ext = (os.path.splitext(self.mayaOutputPath)[1]).split('.')[1]
        if self.mayaOutputPath.rsplit('.', 1)[1]:
            ext = self.mayaOutputPath.rsplit('.', 1)[1]
        else:
            ext = "avi"
        self.playblastPath, playblast_version = self.formatOutputPath(ext)
        self._app.logger.debug("formatted playblastPath = {}".format(self.playblastPath))

        # # check if any version of the published file exists on shotgun
        # versioned_pb_path = self.check_published_version()
        # self._app.logger.debug("createPlayblast: versioned_pb_path = {}".format(versioned_pb_path))

        if os.path.exists(self.mayaOutputPath):
            self._app.logger.debug("createPlayblast: going to copy to formatted path")
            result = shutil.move(self.mayaOutputPath, self.playblastPath)
            self._app.logger.debug("createPlayblast: shutil.move result = {}".format(result))

        publish_name = os.path.basename(self.playblastPath)
        pbname, fileext = os.path.basename(self.playblastPath).split(".")
        self.uploadToShotgun(publish_name= pbname[:-5],
                             version_number=playblast_version)

        return self.playblastPath

    def formatOutputPath(self, ext):
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

        # TODO: condn to check if its a shot context or not
        # TODO: warning if its not a shot context?
        # context = self.getContextInfo()
        template = None

        # path_cache = tank.path_cache.PathCache(self._tk)
        # path_cache_location = path_cache._get_path_cache_location()
        # self._app.logger.debug("path_cache_location = {}".format(path_cache_location))
        # path_cache.close()
        # os.remove(path_cache_location)

        try:
            folders = self._tk.create_filesystem_structure("Task", self._context.task["id"])
            self._app.logger.debug("folders created = {}".format(folders))
            self._app.logger.debug("create_filesystem_structure done")
        except:
            print(Exception)
            self._app.logger.debug("create_filesystem_structure failed")

        print("print in maya - self.playblastParams.keys()) = {}".format(self.playblastParams.keys()))
        print("print in maya - self.playblastParams.values()) = {}".format(self.playblastParams.values()))

        if str(self.playblastParams.get('format')) == "image":
            template = self._tk.templates["playblast_image"]
        elif str(self.playblastParams.get('format')) == "avi":
            template = self._tk.templates["playblast_mov"]
        else:
            self._app.logger.error("playblast format not supported")

        fields = self._context.as_template_fields(template)
        pprint.pprint(fields)
        self._app.logger.debug("fields: {}".format(fields))

        # TODO: generated path's ext
        # ext = (os.path.splitext(self.mayaOutputPath)[1]).split('.')[1]
        fields["ext"] = ext
        fields["publish_type"] = self.publish_type
        fields["plate_name"] = self.getPlateName()
        fields["height"] = int(self.playblastParams['height'])
        fields["width"] = int(self.playblastParams['width'])
        fields["version"] = self.get_next_version_number(template, fields)
        # TODO: pass_type: based on what? cam type from ui
        fields["pass_type"] = 'pass_type'
        print ("field values assigned", fields)

        self._app.logger.debug("fields assigned: {}".format(fields))
        fields.keys()
        publishPath = template.apply_fields(fields)
        self._app.logger.debug("get_playblast_ver(): 1) publishPath: {}".format(publishPath))

        # ver_result = self.get_playblast_ver(publishPath)
        # self._app.logger.debug("ver_result = {}".format(ver_result))
        # # replace with correct version number:
        # fields["version"] = ver_result
        # self._app.logger.debug("get_playblast_ver(): fields (updated version): {}".format(fields))
        # publishPath = template.apply_fields(fields)
        # self._app.logger.debug("get_playblast_ver(): 2) publishPath (updated version): {}".format(publishPath))

        publishPath = "".join(publishPath.split(" "))  # remove whitespaces causing windows os errors
        try:
            self._app.logger.debug("trying sgtk to create the publishPath")
            self._currentEngine.ensure_folder_exists(os.path.dirname(publishPath))
            sgtk.util.filesystem.touch_file(publishPath)
            self._app.logger.debug("sgtk publishPath touched = {}".format(publishPath))
        except:
            if not os.path.exists(os.path.dirname(publishPath)):
                self._app.logger.debug("to create publishPath directories using os")
                os.makedirs(os.path.dirname(publishPath))
                if os.path.isfile(publishPath):
                    self._app.logger.debug("raw_publishPath exists as {}".format(publishPath))
                else:
                    with open(publishPath, 'a'):  # Create file if does not exist
                        os.utime(publishPath, None)
                #Path(raw_publishPath).touch()  # pathlib2 not loading when in shotgun
                # except OSError as exc:  # Guard against race condition
                #     if exc.errno != errno.EEXIST:
                #         raise

            # with open(raw_publishPath, "w") as f:
            #     f.write("FOOBAR")

        return publishPath, fields["version"]

    def get_next_version_number(self, template, fields):
        """
        # Get a list of existing file paths on disk that match the template and provided fields
        # Skip the version field as we want to find all versions, not a specific version.
        :param template:
        :param fields:
        :return:
        """

        skip_fields = ["version"]
        self._app.logger.debug("get_next_version_number: fields = ", fields)

        file_paths = self._tk.paths_from_template(template,
                                                  fields,
                                                  skip_fields,
                                                  skip_missing_optional_keys=True
                                                  )
        versions = []
        for a_file in file_paths:
            # extract the values from the path so we can read the version.
            path_fields = template.get_fields(a_file)
            versions.append(path_fields["version"])

        return max(versions) + 1

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

        self._app.logger.debug("plate_names = {}".format(plate_names))
        return plate_names[0]

    def uploadToShotgun(self, publish_name, version_number):
        """
        To upload the playblast img seq/movie to shotgun
        :return:
        """
        # register new Version entity in shotgun or update existing version

        # Run a Shotgun API query to summarize the maximum version number on PublishedFiles that
        # are linked to the task and match the provided name.
        # Since PublishedFiles generated by the Publish app have the extension on the end of the name we need to add the
        # extension in our filter.

        # todo: version update and use publishPath (check fields first)
        sgtk.util.register_publish(
                                    self._tk,
                                    self._context,
                                    self.playblastPath,
                                    publish_name,
                                    version_number,
                                    comment='test playblast publish try 1',
                                    published_file_type=self.publish_type
                                )

        self._app.log_info("Playblast uploaded to shotgun")

