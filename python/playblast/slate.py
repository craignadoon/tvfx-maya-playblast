import datetime
import shutil
import subprocess

import os
import sys
import argparse
import tempfile
import OpenImageIO


class Slate(object):
    BLANK_SLATE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'track_slate.png'))
    FONT_SCALE = 0.0090
    LINE_SPACING = 60
    LINE_LENGTH = 70

    def __init__(self, app, playblastParams, playblast_path, focal_length):
        """
        Construction
        """
        self.parent = None
        self._app = app
        self.pb_params = playblastParams
        self.pb_path = playblast_path
        self.pb_focal_length = focal_length
        self.slate_data = None

    def create_slate(self, playblast_path, slate_data):
        """
        main function to create slate
        """
        self.slate_data = slate_data
        self.pb_path = playblast_path

        start_time = self.slate_data['start_time']
        self._app.logger.debug("create_slate: start_time = {}".format(start_time))
        self._app.logger.debug("create_slate: self.pb_path = {}".format(self.pb_path))
        self._app.logger.debug("create_slate: self.pb_path % start_time = {}".format(self.pb_path % start_time))

        first_frame_path = self.pb_path % start_time
        self._app.logger.debug("create_slate: first_frame_path = {}".format(first_frame_path))

        slate_path = os.path.join(tempfile.mkdtemp(), 'slate.jpg')
        self._app.logger.debug("create_slate: slate_path (1) = {}".format(slate_path))

        internal_args = self._create_slate_args()
        internal_args += self._generate_ffmpeg_stuff(categories=True, client=False)
        internal_args += self._generate_ffmpeg_stuff(categories=False, client=False)

        if internal_args[-1] == ',':
            internal_args = internal_args[:-1]

        ffmpeg_args = ['ffmpeg', '-y', '-i', self.BLANK_SLATE_PATH, '-i', first_frame_path,
                       '-filter_complex', internal_args, slate_path]

        proc = subprocess.Popen(ffmpeg_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        slate_path = self._match_resolution(slate_path, first_frame_path)
        self._app.logger.debug("create_slate: slate_path (2) = {}".format(slate_path))

        return slate_path

    def create_internal_mov(self, slate, first_frame):
        # self._create_internal_slate()
        slate_frame_number = first_frame - 1
        slate_path = self.pb_path % slate_frame_number

        shutil.copyfile(slate, slate_path)
        internal_mov_path = self.create_mov_from_images(slate_frame_number)

        os.remove(slate_path)
        return internal_mov_path

    def create_mov_from_images(self, first):
        mov_path = os.path.join(tempfile.mkdtemp(), 'mov.mov')
        frame_rate = self.slate_data['frame_rate']
        self._app.logger.debug("frame_rate:{}".format(frame_rate))
        camera = self.slate_data['camera']
        focal = self.slate_data['focal_length']
        artist = self.slate_data['artist']
        shotname = self.slate_data['shot_name']
        project = self.slate_data['project_name']

        # ffmpeg_args = ['ffmpeg',
        #                '-y',
        #                '-start_number', str(first),
        #                # '-framerate', str(frame_rate),
        #                '-filter_complex',
        #                'pad=ceil(iw/2)*2:ceil(ih/2)*2,'
        #                'drawtext='
        #                'start_number={first}:'
        #                'text=FrameNo-%{n}__{focal}mm__{cam}_Camera:'
        #                'fontcolor=white:'
        #                'fontsize=0.025*h:'
        #                'x=w*0.975-text_w:'
        #                'y=h*0.95'.format(first=first, n='{n}', focal=focal, cam=camera),
        #                '-i', self.pb_path,
        #                mov_path,
        #                ]

        # drawtext_string = ("drawtext=start_number=1001:"
        #                    "fontfile=C:\Windows\Fonts\Calibri.ttf:text='%%{n}':"
        #                    "x=w*0.98-text_w:y=h*0.92:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.4,"
        #                    "drawtext=fontfile=C:\Windows\Fonts\Calibri.ttf:start_number=1001:text='35mm':"
        #                    "x=w*0.98-text_w:y=h*0.88:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.4,"
        #                    "drawtext=fontfile=C:\Windows\Fonts\Tahoma.ttf:text='DBR_110_007_666_cam_122f':"
        #                    "x=w*0.35:y=h*0.92:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.4,"
        #                    "drawtext=fontfile=C:\Windows\Fonts\Tahoma.ttf:text='redf_emerald_hill':"
        #                    "x=w*0.42:y=h*0.02:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.4,"
        #                    "drawtext=fontfile=C:\Windows\Fonts\Calibri.ttf:text='artistname':"
        #                    "x=w*0.02:y=h*0.92:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.4,"
        #                    "drawtext=text='2021-04-23':x=w*0.90:y=h*0.02:"
        #                    "fontsize=16:fontcolor=white:box=1:boxcolor=black@0.4").format()
        # drawtext_string = ("select='not(eq(n\,{first})',drawtext=start_number={first}:"
        # drawtext_string = ("select='not(n=0)',drawtext=start_number={first}:"
        drawtext_string = ("select='gte(n\,0)',drawtext=start_number={first}:"
                           "fontfile=C:\Windows\Fonts\Calibri.ttf:text='%{n}':"
                           "x=w*0.98-text_w:y=h*0.92:fontsize=20:fontcolor=white,"
                           "drawtext=fontfile=C:\Windows\Fonts\Calibri.ttf:start_number={first}:text='{focal}mm':" 
                           "x=w*0.98-text_w:y=h*0.88:fontsize=14:fontcolor=white,"
                           "drawtext=fontfile=C:\Windows\Fonts\Tahoma.ttf:text='{shotname}':"
                           "x=w*0.35:y=h*0.92:fontsize=16:fontcolor=white,"
                           "drawtext=fontfile=C:\Windows\Fonts\Tahoma.ttf:text='{project}':"
                           "x=w*0.42:y=h*0.02:fontsize=16:fontcolor=white,"
                           "drawtext=fontfile=C:\Windows\Fonts\Calibri.ttf:text='{artist}':"
                           "x=w*0.02:y=h*0.92:fontsize=16:fontcolor=white," 
                           "drawtext=fontfile=C:\Windows\Fonts\Calibri.ttf:text='{camera}':"
                           "x=w*0.02:y=h*0.02:fontsize=16:fontcolor=white," 
                           "drawtext=text='2021-04-23':x=w*0.90:y=h*0.02:"
                           "fontsize=16:fontcolor=white:box=1:boxcolor=black@0.4").format(first=first,
                                                                                          n='{n}',
                                                                                          focal=focal,
                                                                                          project=project,
                                                                                          shotname=shotname,
                                                                                          artist=artist,
                                                                                          camera=camera)
        self._app.logger.debug("drawtext_string={}".format(drawtext_string))
        # ffmpeg_args = ['ffmpeg',
        #                '-y',
        #                '-start_number', str(first),
        #                '-i', self.pb_path,
        #                '-vf',
        #                drawtext_string,
        #                mov_path,
        #                ]
        ffmpeg_args = ['ffmpeg',
                       '-y',
                       '-start_number', str(first),
                       '-i', self.pb_path,
                       '-vf',
                       # 'select = "gte(n\, 1)"',
                       # 'select = "not(eq(n\,3)"',
                       drawtext_string,
                       mov_path,
                       ]


        self._app.logger.debug("Trying {}".format(' '.join(ffmpeg_args)))

        try:
            proc = subprocess.Popen(ffmpeg_args,shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            _stdout, _stderr = proc.communicate()
            self._app.logger.debug('stdout is: {}'.format(_stdout))
            self._app.logger.debug('stderr is: {}'.format(_stderr))
        except Exception as e:
            self._app.logger.debug("An exception was encountered:")
            self._app.logger.debug(e)
            mov_path = None

        return mov_path

    def _generate_ffmpeg_stuff(self, categories, client):
        ffmpeg_stuff = ''

        template = ("drawtext="
                    "text={text}:"
                    "fontcolor=white:"
                    "fontsize={font_scale}*h:"
                    "fontfile=/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf:"
                    "x=w*0.125{x_offset}:"
                    "y=h*{y_offset}+{i}*{line_spacing},"
                    )

        if categories:
            index = 0
            x_offset = '-text_w'
        else:
            index = 1
            x_offset = ''

        lines = self._set_internal_slate_lines()
        y_offset = 0.425

        for i, line in enumerate(lines):
            if i == 0:
                scale = self.FONT_SCALE * 2
                spacing = self.LINE_SPACING
            elif i == 1:
                scale = self.FONT_SCALE
                spacing = self.LINE_SPACING * 2
            else:
                scale = self.FONT_SCALE
                spacing = self.LINE_SPACING
                i += 1

            ffmpeg_stuff += template.format(text=line[index],
                                            font_scale=scale,
                                            line_spacing=spacing,
                                            x_offset=x_offset,
                                            y_offset=y_offset,
                                            i=i)

        return ffmpeg_stuff

    def _set_internal_slate_lines(self):

        internal_slate_lines = [
            ("'Name\:\ '", "'{name}'".format(name=self.slate_data['project_name'])),
            ("'Project ID\:\ '", "'{id}'".format(id=self.slate_data['project_id'])),
            ("'Shot ID\:\ '", "'{id}'".format(id=self.slate_data['shot_id'])),
            ("'Shot Name\:\ '", "'{name}'".format(name=self.slate_data['shot_name'])),
            ("'Version\:\ '", "'{version}'".format(version=self.slate_data['playblast_version'])),
            ("'Frames\:\ '", "'{first}-{last} ({range}f)'"
             .format(first=self.pb_params['startTime'],
                     last=self.pb_params['endTime'],
                     range=self.pb_params['endTime'] - self.pb_params['startTime'] + 1)),
            ("'Resolution\:\ '", "'{w}x{h}'".format(w=self.pb_params['width'],
                                                      h=self.pb_params['height'])),
            ("'Focal Length\:\ '", "'{focal} mm'".format(focal=self.slate_data['focal_length'])),
            ("''", "''"),
            ("'Artist\:\ '", "'{artist}'".format(artist=self.slate_data['artist'])),
            ("'Date\:\ '", "'{date}'".format(date=datetime.date.today())),
            # ("'Time Log\:\ '", "'{time_log} hours'".format(time_log=self._time_log)),
            ("''", "''"),
            # ("'Notes\:\ '", "'{notes}'".format(notes=comment)),
        ]
        return internal_slate_lines

    def _create_slate_args(self):
        aspect_ratio = float(self.pb_params['width'] / self.pb_params['height'])

        if aspect_ratio > 1:
            width = 'w=iw*0.25:'
            height = 'h=ow/mdar:'
        else:
            width = 'w=oh*mdar:'
            height = 'h=ih*0.25:'

        x = 0.775
        y = 0.5

        ffmpeg_args = (
            # add white border to plate
            "[1:v]"
            "pad="
            "iw*1.01:"
            "ih*1.01:"
            "iw/1.01:"
            "ih/1.01:"
            "color=white"
            "[border_plate];"
            # scale plate to correct size
            "[border_plate][0:v]"
            "scale2ref="
            "{width}"
            "{height}"
            "[plate][slate];"
            # add plate to slate
            "[slate][plate]"
            "overlay="
            "main_w*{x}-overlay_w*0.5:"
            "main_h*{y}-overlay_h*0.5,"
        ).format(width=width, height=height, x=x, y=y)

        return ffmpeg_args

    def _match_resolution(self, input_path, target_path):
        output_path = os.path.join(tempfile.mkdtemp(), "resized_plate.jpg")
        other_output_path = os.path.join(tempfile.mkdtemp(), "temp_resized_plate.jpg")
        self._app.logger.debug("_match_resolution: output_path (1) = {}".format(output_path))
        self._app.logger.debug("_match_resolution: other_output_path (1) = {}".format(other_output_path))

        input_buf = OpenImageIO.ImageBuf(str(input_path))
        # OpenImageIO.ImageInput.open(str(input_path)).spec().width

        target_buf = OpenImageIO.ImageBuf(str(target_path))
        target_width = target_buf.roi.width
        target_height = target_buf.roi.height

        resize_width = target_width
        resize_height = target_width
        resize_spec = OpenImageIO.ImageSpec(resize_width,
                                            resize_height,
                                            input_buf.spec().nchannels,
                                            input_buf.spec().format
                                            )

        resize_buf = OpenImageIO.ImageBuf(resize_spec)

        OpenImageIO.ImageBufAlgo.resize(resize_buf, input_buf)

        resize_buf.write(other_output_path)

        output_buf = OpenImageIO.ImageBuf()

        y = (resize_height - target_height) / 2
        OpenImageIO.ImageBufAlgo.crop(output_buf, resize_buf,
                                      OpenImageIO.ROI(0, resize_width,
                                                      y, y + target_height
                                                      )
                                      )

        output_buf.write(output_path)

        return output_path

