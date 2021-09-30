# coding=utf-8
import datetime
import glob
import pprint
import shutil
import subprocess
import tempfile

import os
import re

import OpenImageIO
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import sgtk

import tank
from tank import path_cache
from sgtk.util import filesystem, LocalFileStorageManager

try:
    from sgtk.platform.qt import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui

from .slate import Slate

BASE_DIR_PATH = os.path.dirname(__file__).replace('\\', '/')


class PlayblastManager(object):
    """
    Main playblast functionality
    """

    def __init__(self, app, context=None, emitter=None):
        """
        Construction
        """
        self.parent = None
        self._app = app
        self._context = context if context else self._app.context

        self._currentEngine = sgtk.platform.current_engine()
        self._tk = self._currentEngine.sgtk

        self.emitter = emitter or self._app.logger.info

        # self.status("progress bar here")

        # self._context = currentEngine.context
        if self._context is None:
            self._context = self._currentEngine.context

        self._app.logger.info("Playblast self._context = {}".format(self._context))

        self.publish_type = "Playblast"
        self.pass_type = None
        self.description = None
        self.camera_type = None
        self.focal_length = None
        # self.mayaOutputPath = self.get_temp_output()
        self.mayaOutputPath = None
        self.playblastPath = None
        self.playblast_mov_path = None
        self.playblastParams = {
            'offScreen': False,
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
            'showOrnaments': True,
            'clearCache': True,
            'sequenceTime': False
        }
        self.slate = Slate(self._app, self.playblastParams, self.playblastPath, self.focal_length)
        self.camera_shape = self.get_current_camera()

    def get_context(self):
        """
        method to return current app context
        :return:
        """
        self._app.logger.debug("self._context.entity = {}".format(self._context.entity))
        self._app.logger.debug("self._context.step = {}".format(self._context.step))
        self._app.logger.debug("self._context.task = {}".format(self._context.task))
        return self._context

    def set_pass_type(self, pass_type):
        """
        method to set pass type as per user input in the ui
        :param pass_type: string pass type:  smoothShaded, wireframe, flatShaded, bounding box, and points
        :return:
        """
        self.pass_type = pass_type

    def set_description(self, comment):
        self.description = comment

    def set_camera_type(self, camera_type):
        if camera_type == "perspective":
            self.camera_type = "persp"
        else:
            self.camera_type = camera_type

    def set_focal_length(self, focal_length):
        if focal_length:
            self.focal_length = focal_length
        else: # todo: Confirm default focal length value
            self.focal_length = 35

    def get_temp_output(self, ext):
        if not ext.startswith('.'):
            ext = '.' + ext
        if ext == ".avi":
            self.mayaOutputPath = tempfile.mktemp(suffix=ext, prefix='maya_playblast_')
        else:
            self.mayaOutputPath = tempfile.mktemp(prefix='maya_playblast_')
        self._app.logger.debug("get_temp_output: ext= {0}, self.mayaOutputPath ={1}".format(ext, self.mayaOutputPath))
        return self.mayaOutputPath

    def get_frame_range(self):
        """
        function to get frame range from current maya scene
        :returns:
            start (int): start frame
            end (int): end frame
        """
        start = int(cmds.playbackOptions(q=True, minTime=True))
        end = int(cmds.playbackOptions(q=True, maxTime=True))
        self.emitter("self._context.entity = {}".format(self._context.entity))
        shot_info = self._context.sgtk.shotgun.find_one(self._context.entity['type'],
                                                        [['id', 'is', self._context.entity['id']]],
                                                        ['sg_head_in', 'sg_tail_out'])
        start_frame = int(shot_info['sg_head_in'] or start)
        last_frame = int(shot_info['sg_tail_out'] or end)
        self._app.logger.debug("get_frame_range(): start, end frame = {0}, {1}".format(start_frame, last_frame))

        return start_frame, last_frame

    def createPlayblast(self, override_playblast_params):
        """
        function to call maya's internal playblast command to create playblast
        as per user input in ui.gatherUiData
        :param
            override_playblast_params (dict): user input from ui
        :return:
            playblastPath: output playblast file path.
        """
        self.emitter('Gathering user inputs..')

        self.playblastParams.update(override_playblast_params)
        # TODO: filename
        self._app.logger.debug("&&&&& self.playblastParams():")
        self._app.logger.debug(self.playblastParams)
        # if not self.focus:
        #     self.focus = True
        # panel = self.get_current_panel()
        # self._app.logger.debug("createPlayblast: panel = {}".format(panel))
        # self._app.logger.debug("createPlayblast: self.pass_type = {}".format(self.pass_type))
        # cmds.getPanel(withFocus=True)
        # cmds.modelEditor(panel, edit=True, displayAppearance=self.pass_type)
        self.emitter('Running playblast..!!!!!!!!!!!!!!')

        # adding the HUD For the FL
        cmds.headsUpDisplay(rp=(9, 9))
        cmds.headsUpDisplay('FL99', s=9, b=9, p=20, bs='small', ba='right', da='right', lfs='large', dfs='large', l='',
                            c=self.get_focal_length)

        cmds.expression(n='CUSTOMHUD', s='headsUpDisplay -r FL99;')

        self.mayaOutputPath = cmds.playblast(**self.playblastParams)
        self._app.logger.debug("createPlayblast: mayaOutputPath = {}".format(self.mayaOutputPath))

        cmds.headsUpDisplay(rp=(9, 9))
        cmds.delete('CUSTOMHUD')

        if self.playblastParams['format'] == 'image':
            extension = "jpg"
        else:
            extension = "avi"

        self.playblastPath, playblast_version = self.format_output_path(extension)
        # self.emitter('Getting latest version: {}'.format(playblast_version))
        self._app.logger.debug("formatted playblastPath = {}".format(self.playblastPath))

        if self.playblastParams['format'] == 'image':
            pb_name, padding, file_ext = os.path.basename(self.playblastPath).split(".")
            self._app.logger.debug("pb_name= {0}, padding= {1}, file_ext = {2}".format(pb_name, padding, file_ext))
        else:
            pb_name, file_ext = os.path.basename(self.playblastPath).split(".")
            self.emitter('Getting latest version: {}'.format(playblast_version))
            self._app.logger.debug("pb_name= {0}, file_ext = {1}".format(pb_name, file_ext))

        self._app.logger.debug("self.mayaOutputPath = {}".format(self.mayaOutputPath))
        self._app.logger.debug(os.path.exists(self.mayaOutputPath))

        if file_ext == "avi":
            result = shutil.copyfile(self.mayaOutputPath, self.playblastPath)
        else:
            seq_name, hashes, ext = self.mayaOutputPath.split(".")
            padding = '.%0{}d.'.format(hashes.count('#'))
            self.mayaOutputPath = str(seq_name + padding + ext)
            self._app.logger.debug("self.mayaOutputPath after formatting = {}".format(self.mayaOutputPath))
            self._app.logger.debug("seq_name= {0}, hashes= {1}, ext = {2}".format(seq_name, hashes, ext))

            for i, frame_num in enumerate(range(self.playblastParams['startTime'],
                                                self.playblastParams['endTime'])):
                result = shutil.copy(self.mayaOutputPath % frame_num, self.playblastPath % frame_num)
            self._app.logger.debug("Image sequence copied to playblast path= {}".format(self.playblastPath))
            self.emitter('Image sequence copied to playblast path: {}'.format(self.playblastPath))
            # format the movie path as per template with mov extension
            self.playblastParams['format'] = "mov"
            self.playblast_mov_path, playblast_version = self.format_output_path('mov')
            self.emitter('Getting latest version: {}'.format(playblast_version))
            self.playblastParams['format'] = "image"

            # Create slate
            slate_data = self.gather_slate_data(playblast_version)
            slate = self.slate.create_slate(self.playblastPath, slate_data)
            ffmpeg_mov = self.slate.create_internal_mov(slate, self.playblastParams['startTime'])
            self._app.logger.debug("createPlayblast: ffmpeg_mov = {}".format(ffmpeg_mov))

            result = shutil.copy(ffmpeg_mov, self.playblast_mov_path)

            self._app.logger.debug("self.playblast_mov_path(ffmpeg movie) = {}".format(self.playblast_mov_path))
            pb_name, file_ext = os.path.basename(self.playblast_mov_path).split(".")

        version_entity = self.upload_to_shotgun(publish_name=pb_name[:-5],
                                                version_number=playblast_version)

        return self.playblastPath, version_entity

    def get_current_panel(self):
        """
        get current panel in focus for maya
        :return:
        """
        # panel = cmds.getPanel(withFocus=True)
        #
        # if cmds.getPanel(typeOf=panel) != 'modelPanel':
        #     # just get the first visible model panel we find, hopefully the correct one.
        #     for p in cmds.getPanel(visiblePanels=True):
        #         if cmds.getPanel(typeOf=p) == 'modelPanel':
        #             panel = p
        #             cmds.setFocus(panel)
        #             break
        #
        # self._app.logger.debug("get_current_panel: panel = {}".format(panel))

        # if cmds.getPanel(typeOf=panel) != 'modelPanel':
        #     OpenMaya.MGlobal.displayWarning('Please highlight a camera viewport.')
        #     return False
        # self._app.logger.debug("get_current_panel: self.camera_type = {}".format(self.camera_type))
        self._app.logger.debug("get_current_panel: self.camera_type = {}".format(self.camera_type))
        cam_panel = self.get_panel_from_camera(self.camera_type)
        self._app.logger.debug("get_current_panel: cam_panel = {}".format(cam_panel))

        return cam_panel

    def get_panel_from_camera(self, camera_name):
        """
        To get modal panel wrt the camera.
        this is to avoid cases when no modal plane is selected
        :param camera_name: name of the camera
        :return: panel name
        """
        list_panel = []
        for panel_name in cmds.getPanel(type="modelPanel"):
            if cmds.modelPanel(panel_name, query=True, camera=True) == camera_name:
                self._app.logger.debug("in if condn")
                list_panel.append(panel_name)

        self._app.logger.debug("get_panel_from_camera: list_panel = {}".format(list_panel))

        return list_panel

    def get_maya_window_resolution(self):
        cmds.currentTime(cmds.currentTime(query=True))
        panel = cmds.playblast(activeEditor=True)
        panel_name = panel.split("|")[-1]
        width = cmds.control(panel_name, query=True, width=True)
        height = cmds.control(panel_name, query=True, height=True)
        return width, height

    def get_maya_render_resolution(self):
        width = cmds.getAttr('defaultResolution.width')
        height = cmds.getAttr('defaultResolution.height')
        return width, height

    def format_output_path(self, ext):
        """
        function to format output file path as per template.
            maya_playblast_publish_image
            maya_playblast_publish_mov
        in templates.yml in config
        :return:
             publishPath: formatted output file path
        """

        # TODO: condn to check if its a shot context or not
        # TODO: warning if its not a shot context?
        # context = self.getContextInfo()
        template = None

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
        elif str(self.playblastParams.get('format')) == "avi" or "mov":
            template = self._tk.templates["playblast_mov"]
        else:
            self._app.logger.error("playblast format not supported")

        fields = self._context.as_template_fields(template)
        pprint.pprint(fields)
        self._app.logger.debug("fields: {}".format(fields))

        # TODO: generated path's ext
        fields["ext"] = ext
        fields["publish_type"] = self.publish_type
        fields["plate_name"] = self.get_plate_name()
        fields["height"] = int(self.playblastParams['height'])
        fields["width"] = int(self.playblastParams['width'])
        fields["version"] = 0
        # self.get_next_version_number(template, fields)
        fields["pass_type"] = self.pass_type
        print ("field values assigned", fields)

        self._app.logger.debug("fields assigned: {}".format(fields))
        publishPath = template.apply_fields(fields)
        self._app.logger.debug("get_playblast_ver(): 1) publishPath: {}".format(publishPath))

        # fetch latest publish version from shotgun and apply the incremented version to publish path
        published_version = self.get_published_version(publishPath, self.publish_type)
        fields["version"] = published_version
        publishPath = template.apply_fields(fields)

        publishPath = "".join(publishPath.split(" "))  # remove whitespaces causing windows os errors
        # create folders and touch the publish file path
        try:
            self._app.logger.debug("trying sgtk to create the publishPath")
            self._currentEngine.ensure_folder_exists(os.path.dirname(publishPath))
            sgtk.util.filesystem.touch_file(publishPath % (self.playblastParams['startTime']))
            self._app.logger.debug("sgtk publishPath touched = {}".format(publishPath))
        except:
            if not os.path.exists(os.path.dirname(publishPath)):
                self._app.logger.debug("Creating publishPath directories using os module")
                os.makedirs(os.path.dirname(publishPath))
                if os.path.isfile(publishPath):
                    self._app.logger.debug("publishPath exists as {}".format(publishPath))
                else:
                    with open(publishPath, 'a'):  # Create file if does not exist
                        os.utime(publishPath, None)

        self._app.logger.debug("format_output_path: published_version = {}".format(published_version))
        self._app.logger.debug("format_output_path: fields[version] = {}".format(fields["version"]))

        return publishPath, fields["version"]

    def get_published_version(self, path, publish_type=None, increment=True):
        """
        checks for existing versions of playblast path on shotgun and increments the value by 1,
        if there is a match on shotgun for the given context and fields.
        returns the new playblast version after
        :param path :           path to the playblast output formatted as per template
        :param publish_type :   type of published file. In our case, "Playblast"
        :param increment :      bool to decide if we increment the version number or not.Yes in our case
        :return:                version of the new published playblast file
        """
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
        publish_type = self.publish_type
        publisher = self._currentEngine.apps.get("tk-multi-publish2")
        # ensure we have the publisher instance.
        if not publisher:
            raise Exception("The publisher is not configured for this context.")
        path_info = publisher.util.get_file_path_components(path)
        filename = path_info['filename']
        # # VERSION_REGEX = r'v\s*([\d]+)'
        # VERSION_REGEX = r'v(\d)+'
        # version_pattern_match = re.search(VERSION_REGEX, os.path.basename(filename))
        # if not version_pattern_match:
        #     error_msg = "Not able to detect version from given path: %s" % filename
        #     raise ValueError(error_msg)
        # # found a version number, use the other groups to remove it
        # x = version_pattern_match.group(0)
        # prefix = version_pattern_match.group(1)
        # extension = version_pattern_match.group(4) or ""
        # TODO:replace string manipulations with a regex to extract filename without version and extension
        self._app.logger.debug("filename = {0}".format(filename))
        if self.playblastParams.get('format') == 'image':
            name, padding, extension = filename.rsplit('.')
        else:
            name, extension = filename.rsplit('.')
        # self._app.logger.debug("get_playblast_ver:extension={0}, prefix = {1}, x ={2} ".format(extension, prefix, x))
        self._app.logger.debug("filename = {0}, name = {1}".format(filename, name[:-5]))

        # build filters now
        # code: published file name (no ext/ver)
        filters.append(
            ['code', 'starts_with', name[:-5]],
        )
        # ext: version for ext
        if extension:
            filters.append(['code', 'ends_with', extension])
        # publish_type: Playblast publish type
        if publish_type:
            filters.append(
                ['published_file_type.PublishedFileType.code', 'is', publish_type]
            )

        self._app.logger.debug("get_playblast_ver: filters = {}".format(filters))

        # Run a Shotgun API query to summarize the maximum version number on PublishedFiles that
        # are linked to the task and match the provided name.
        # Since PublishedFiles generated by the Publish app have the extension on the end of the name we need to add the
        # extension in our filter.

        # r = self._currentEngine.shotgun.summarize(entity_type="PublishedFile",
        #                                           filters=filters,
        #                                           # [["task", "is", {"type": "Task", "id": self._context.task["id"]}],
        #                                           #     ["name", "is", fields["name"] + ".avi"]],
        #                                           summary_fields=[{"field": "version_number", "type": "maximum"}])
        # publish_version = r["summaries"]["version_number"] + 1

        available_records = publisher.sgtk.shotgun.find_one(
            entity_type='PublishedFile',
            filters=filters,
            fields=['version_number'],
            order=[{'field_name': 'version_number', 'direction': 'desc'}]
        )
        self._app.logger.debug("available_records = {}".format(available_records))
        if available_records:
            latest_version = available_records['version_number']
        else:
            latest_version = 0
        if increment:
            latest_version += 1

        self._app.logger.debug("get_published_version: latest_version = {}".format(latest_version))
        return latest_version

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

        if versions:
            return max(versions) + 1
        else:
            return 1

    def get_plate_name_from_entity(self, entity):
        """Parses plate's PublishedFile entity and returns plate name
        Args:
            entity(dict): PublishedFile entity of type plate
        Returns:
            str: plate name
        """
        pattern = re.compile('\S+\w+')

        description = entity.get('description') or ''
        description = description.split('\n')[-1]
        details = pattern.findall(description)
        if details:
            return details[1]
        return ''

    def get_plate_name(self):
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

    # def create_version_entity(self, publish_name):
    #     self.emitter('Creating version entity')
    #     playblast_version_entity = self._context.sgtk.shotgun.create(
    #         'Version',
    #         {
    #             'code': publish_name,
    #             # 'code': os.path.splitext(os.path.basename(movie_path))[0],
    #             'entity': self._context.entity,
    #             'project': self._context.project,
    #             'user': self._context.user,
    #             'description': self.description,  # 'Version creation from playblast tool',
    #             'sg_path_to_movie': self.playblastPath,
    #             # 'sg_path_to_frames': str(published_plate),
    #             'sg_version_type': 'Artist Version',
    #         }
    #     )
    #     self._context.sgtk.shotgun.upload(
    #         'Version', playblast_version_entity['id'], self.playblastPath, 'sg_uploaded_movie'
    #     )
    #     self._app.logger.debug('version_entity: {}', playblast_version_entity)
    #
    #     return playblast_version_entity
    #
    def upload_to_shotgun(self, publish_name, version_number):
        """
        To upload the playblast img seq/movie to shotgun

        :return:
        """
        # register new Version entity in shotgun or update existing version
        self.emitter('Uploading media to Shotgun entity')

        self._app.logger.debug('MOV PATH FOR VERSION ENTITY: format = {}'.format(self.playblastParams['format']))
        if self.playblastParams['format'] == 'image':
            self._app.logger.debug('self.playblast_mov_path: {}'.format(self.playblast_mov_path))
            movie_to_upload = self.playblast_mov_path
        else:
            self._app.logger.debug('playblastPath: {}'.format(self.playblastPath))
            movie_to_upload = self.playblastPath

        playblast_version_entity = self._context.sgtk.shotgun.create(
            'Version',
            {
                'code': publish_name,
                # 'code': os.path.splitext(os.path.basename(movie_path))[0],
                'entity': self._context.entity,
                'project': self._context.project,
                'user': self._context.user,
                'description': self.description,  # 'Version creation from playblast tool',
                'sg_path_to_movie': movie_to_upload,
                # 'sg_path_to_frames': str(published_plate),
                'sg_version_type': 'Artist Version',
            }
        )
        self._context.sgtk.shotgun.upload(
            'Version', playblast_version_entity['id'], movie_to_upload, 'sg_uploaded_movie'
        )
        self._app.logger.debug('version_entity: {}', playblast_version_entity)

        self.emitter('Registering playblast on shotgun as PublishedFile..')
        sgtk.util.register_publish(
            self._tk,
            self._context,
            movie_to_upload,
            publish_name,
            version_number,
            comment=self.description,
            published_file_type=self.publish_type,
            version_entity=playblast_version_entity
        )

        self._app.log_info("Playblast uploaded to shotgun")

        return playblast_version_entity

    def gather_slate_data(self, playblast_version):
        context = self._context
        data = {
            'project_name': context.project['name'],
            'project_id': context.project['id'],
            'shot_name': context.entity['name'],
            'shot_id': context.entity['id'],
            'start_time': self.playblastParams['startTime'],
            'playblast_version': playblast_version,
            'focal_length': self.focal_length,
            'artist': context.user['name'],
            'frame_rate': self.get_frame_rate(),
            'camera': self.camera_type
        }
        return data

    def get_frame_rate(self):
        """
        Return an int of the current frame rate
        """
        currentUnit = cmds.currentUnit(query=True, time=True)
        if currentUnit == 'film':
            return 24
        if currentUnit == 'show':
            return 48
        if currentUnit == 'pal':
            return 25
        if currentUnit == 'ntsc':
            return 30
        if currentUnit == 'palf':
            return 50
        if currentUnit == 'ntscf':
            return 60
        if 'fps' in currentUnit:
            return int(currentUnit.substitute('fps', ''))

        return 1

    def get_focal_length_min_max(self):
        key_values = cmds.keyframe('%s.focalLength' % self.camera_shape, q=True, vc=True)
        if key_values and len(key_values) > 1:
            key_values = set(key_values)
            return '%s - %s mm' % (min(key_values), max(key_values))
        else:
            return '%s mm' % cmds.getAttr('%s.focalLength' % self.camera_shape)

    def get_focal_length(self):
        # self.emitter('self.camera_shape.. %s' % self.camera_shape)
        if self.camera_shape:
            return '%smm' % round(float(cmds.getAttr('%s.focalLength' % self.camera_shape)), 2)
        else:
            return '%smm' % self.focal_length

    def get_current_camera(self):
        panel = cmds.getPanel(withFocus=True)

        if cmds.getPanel(typeOf=panel) != 'modelPanel':
            for p in cmds.getPanel(visiblePanels=True):
                if cmds.getPanel(typeOf=p) == 'modelPanel':
                    panel = p
                    cmds.setFocus(panel)
                    break

        if cmds.getPanel(typeOf=panel) != 'modelPanel':
            OpenMaya.MGlobal.displayWarning('Please highlight a camera viewport.')
            return False

        cam_shape = cmds.modelEditor(panel, query=True, camera=True)
        if not cam_shape:
            return False

        if cmds.nodeType(cam_shape) == 'transform':
            return cmds.listRelatives(cam_shape, c=True, path=True)[0]

        return cam_shape

    @property
    def client_info(self):

        client_info = self._context.sgtk.shotgun.find_one(
            'CustomNonProjectEntity30', [['sg_projects', 'is', self._context.project]], ['sg_client_code'])

        return client_info

    def get_defaults_values(self):
        from tank_vendor import yaml
        client_code = self.client_info['sg_client_code']
        setting_yaml_file = BASE_DIR_PATH.replace('/python/playblast', '/resources/defaults.yml')
        fopen = open(setting_yaml_file)
        yaml_data = yaml.load(fopen)
        client_data = yaml_data[client_code] if client_code in yaml_data else yaml_data['default_options']

        return client_data['camera_type'], client_data['pass_type'], client_data['frame_padding'], client_data['scale']
