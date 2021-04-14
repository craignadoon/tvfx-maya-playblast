# coding=utf-8
import errno

# from pathlib2 import Path
# import pathlib2
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

        #taskPath = r'X:\Projects\test_test\sequences\rd\FTWD_0611_035_0020\track\work\maya\FTWD_0611_035_0020_track_weirdBall_v001.npawar.ma'
        #tk = sgtk.sgtk_from_path(taskPath)
        #tk = currentEngine.sgtk

        # self._app.logger.debug("tk = {}".format(tk))
        #     self._app = sgtk.platform.current_bundle()
        #     self._current_engine = sgtk.platform.current_engine()
        #     self._context = self._current_engine.context
        #     self._shotgun = self._current_engine.shotgun
        #     self._toolkit = self._current_engine.sgtk

    def get_temp_output(self, ext):
        # if self._context.entity:
        #     return os.path.
        #         self._context.entity.mov
        # else:
        #     return self._context.task
        # Entity: {'type': 'Shot', 'id': 11130, 'name': 'FTWD_0611_035_0020'}
        # Step: {'type': 'Step', 'id': 2, 'name': 'Tracking'}
        # Task: {'type': 'Task', 'name': 'test_playblast', 'id': 33404}
        # "/{Shot}_{Step}_{pass_type}_[{name}_]v{version}[.{framecount}f].{ext}"
        ver = 0
        # temp_playblast = tempfile.NamedTemporaryFile(prefix="{0}_{1}_playblast".format(
        #     self._context.entity['name'],
        #     self._context.step['name']),
        #     suffix="v{0}.{1}".format(('%03d' % ver), ext))

        # temp = tempfile.NamedTemporaryFile(delete=False, suffix='.mov')

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
        # temp_dir = 'C:\\work\\tempPlayblast\\'
        # temp_playblast = "{0}_{1}_playblast_v{2}.{3}".format(
        #                         self._context.entity['name'],
        #                         self._context.step['name'],
        #                         ('%03d' % ver),
        #                         ext)

        self._app.logger.debug("get_temp_output: maya temp output file = {}".format(self.mayaOutputPath))
        # 'c:\\users\\navpreet\\appdata\\local\\temp\\FTWD_0611_035_0020//Tracking cn9nijv0.avi'
        # return temp_playblast.name
        #
        # if os.path.exists(temp_dir):
        #     return temp_dir+str(temp_playblast)
        # else:
        #     return "C:\\Desktop\\"+str(temp_playblast)

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
        as per user input in ui.gatherUiData
        :param
            overridePlayblastParams (dict): user input from ui
        :return:
            playblastPath: output playblast file path.
        """
        # filename = "C:/work/tempPlayblast/mayaplayblast.mov"
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
        self.playblastPath = self.formatOutputPath(ext)
        self._app.logger.debug("formatted playblastPath = {}".format(self.playblastPath))




        if os.path.exists(self.mayaOutputPath):
            self._app.logger.debug("createPlayblast: going to copy to formatted path")
            result = shutil.move(self.mayaOutputPath, self.playblastPath)
            self._app.logger.debug("createPlayblast: shutil.move result = {}".format(result))

        # check if any version of the published file exists on shotgun
        # version = self.get_playblast_ver(self.playblastPath)
        # self._app.logger.debug("version = {}".format(version))

        return self.playblastPath

    def formatOutputPath(self, ext):
    # def formatOutputPath(self):

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
        # self._app.logger.debug\
        print("print in maya - self.playblastParams.keys()) = {}".format(self.playblastParams.keys()))
        print("print in maya - self.playblastParams.values()) = {}".format(self.playblastParams.values()))
        pprint.pprint(self.playblastParams)
        if str(self.playblastParams.get('format')) == "image":
            print "in if"
            template = self._tk.templates["playblast_image"]
        elif str(self.playblastParams.get('format')) == "avi":
            print "in elif"
            template = self._tk.templates["playblast_mov"]
        else:
            print("playblast.get(format) didnot find the formats")
            self._app.logger.error("playblast format not supported")

        # template = self._tk.templates["maya_shot_publish"]
        # pprint.pprint("template = ", template)
        fields = self._context.as_template_fields(template)
        pprint.pprint(fields)
        self._app.logger.debug("fields: {}".format(fields))
        # from the input: ['publish_type', 'plate_name',
        # 'ext', 'height', 'width', 'version', 'pass_type']

        # publish_type = ['Geometry', 'Locator', 'Camera', 'Lense', '2DTracks']
        # if self.playblastParams['format'] == "image":
        #     fields["ext"] = "jpg"
        # else:
        #     fields["ext"] = "mov"
        fields["publish_type"] = self.publish_type
        # TODO: generated path's ext
        # print ("self.mayaOutputPath =", self.mayaOutputPath )
        # ext = (os.path.splitext(self.mayaOutputPath)[1]).split('.')[1]
        fields["ext"] = ext
        fields["plate_name"] = self.getPlateName()
        fields["height"] = int(self.playblastParams['height'])
        fields["width"] = int(self.playblastParams['width'])

        # fields["version"] = self.get_playblast_ver(self.mayaOutputPath,
        #                                            publish_type=self.publish_type,
        #                                            increment=True)
        fields["version"] = 000
        # TODO: pass_type: based on what? cam type from ui
        fields["pass_type"] = 'pass_type'
        print ("field values assigned")

        publishPath = template.apply_fields(fields)

        self._app.logger.debug("publishPath: {}".format(publishPath))
        #publishPath =
        #self._currentEngine.ensure_folder_exists(os.path.dirname(publishPath))



        # try:
        #
        #     raw_publishPath = "%r" % publishPath
        #     sgtk.util.filesystem.touch_file(raw_publishPath)
        #     self._app.logger.debug("publishPath touched = {}".format(raw_publishPath))
        # except OSError:
        #     self._app.logger.error("some errrorr with file creation!!")
        #     self._app.logger.error(OSError)
        # raw_publishPath = '%r' % publishPath

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

        return publishPath

    def get_playblast_ver(self, path, publish_type=None, increment=True):
        """

        :return:
        """
        # return 3

        filters = []
        # check if we have required context to work with
        if not self._context.entity:
            error_msg = 'No linked Shot/Asset found with current context: %r' % self._context
            self._app.logger.error(error_msg)
            raise EnvironmentError(error_msg)
        else:
            filters.append(
                ['entity', 'is', self._context.entity]
            )
        if not self._context.project:
            error_msg = 'No linked Project found with current context: %r' % self._context
            self._app.logger.error(error_msg)
            raise EnvironmentError(error_msg)
        else:
            filters.append(
                ['project', 'is', self._context.project]
            )
        self._app.logger.debug("get_playblast_ver: filters = {}".format(filters))

        # get path info
        # context = publisher.context
        # logger = publisher.logger
        publish_type = self.publish_type
        # publisher = self.parent
        publisher = self._currentEngine.apps.get("tk-multi-publish2")
        # ensure we have the publisher instance.
        if not publisher:
            raise Exception("The publisher is not configured for this context.")
        path_info = publisher.util.get_file_path_components(path)
        filename = path_info['filename']
        VERSION_REGEX = r'v\s*([\d]+)'
        version_pattern_match = re.search(VERSION_REGEX, os.path.basename(filename))
        if not version_pattern_match:
            error_msg = "Not able to detect version from given path: %s" % filename
            raise ValueError(error_msg)
        # found a version number, use the other groups to remove it
        prefix = version_pattern_match.group(1)
        # extension = version_pattern_match.group(4) or ""
        extension = filename.rsplit('.', 1)[1]
        self._app.logger.debug("get_playblast_ver: extension = {0}, prefix = {1}".format(extension, prefix))
        # build filters now
        filters.append(
            ['code', 'starts_with', prefix],
        )
        # code: published file name (no ext/ver)
        # ext: version for ext
        if extension:
            filters.append(['code', 'ends_with', extension])
        if publish_type:
            filters.append(
                ['published_file_type.PublishedFileType.code', 'is', publish_type]
            )
        available_records = publisher.sgtk.shotgun.find_one(
            entity_type='PublishedFile',
            filters=filters,
            fields=['version_number'],
            order=[{'field_name': 'version_number', 'direction': 'desc'}]
        )
        if available_records:
            latest_version = available_records['version_number']
        else:
            latest_version = 0
        if increment:
            latest_version += 1
        return latest_version

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

