import os
import uuid
import shutil
import urllib

import pytube
import vimeo_dl as vimeo

from deepstar.filesystem.video_dir import VideoDir
from deepstar.filesystem.video_file import VideoFile
from deepstar.models.video_model import VideoModel
from deepstar.plugins.plugin import Plugin
from deepstar.util.command_line_route_handler import CommandLineRouteHandler
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError
from deepstar.util.debug import debug
from deepstar.util.parse import parse_range
from deepstar.util.tempdir import tempdir
from deepstar.util.video import create_one_video_file_from_one_image_file


def pytube_on_progress_callback(stream, chunk, file_handle, bytes_remaining):
    """
    This function is called by putube as a video is downloaded and is used to
    print download progress.

    :rtype: None
    """

    t = f'{(1.0 - bytes_remaining / stream.filesize) * 100.0:3.2f}%'.zfill(7)

    debug(t, 4)


class VideoCommandLineRouteHandler(CommandLineRouteHandler):
    """
    This class implements the VideoCommandLineRouteHandler class.
    """

    def uuid(self):
        """
        This method wraps uuid.uuid4 to ease testing.

        :rtype: str
        """

        return str(uuid.uuid4())

    def insert_file(self, path, opts={}):
        """
        This method inserts a local video into the video colletion.

        :param str path: The path to the video.
        :param dict opts: The optional dict of options.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        if not os.path.isfile(path):
            raise CommandLineRouteHandlerError(
                f'File {path} not found')

        filename = self.uuid() + os.path.splitext(path)[1]

        shutil.copy(path, VideoDir.path() + '/' + filename)

        desc = opts.get('description', None)

        video_id = VideoModel().insert(path, filename, desc)

        debug(f'video_id={video_id}, uri={path}, filename={filename}, '
              f'description={desc}', 3)

    def youtube_context(self, url):
        """
        This method returns an instance of the pytube.YouTube class.

        :param str url: The URL to a YouTube video.
        :rtype: pytube.YouTube
        """

        return pytube.YouTube(url,
                              on_progress_callback=pytube_on_progress_callback)

    def youtube_streams(self, context):
        """
        This methods returns a list of YouTube stream attributes. Fields
        returned include itag, mime_type and res.

        Example:

        [['22', 'video/mp4', '720p']]

        :param pytube.YouTube context: An instance of the pytube.YouTube class.
        :rtype: list(list(str, str, str))
        """

        streams = []

        for stream in context.streams.all():
            streams.append([stream.itag, stream.mime_type, stream.resolution])

        return streams

    def youtube_select(self, streams):
        """
        This method selects a YouTube stream to download.

        :param list(list(str, str, str)) streams: A list of YouTube stream
            attributes.
        :rtype: list(str, str, str)
        """

        selected = None

        for stream in streams:
            if stream[1] == 'video/mp4':
                if selected is None:
                    selected = stream
                else:
                    if stream[2]:
                        # It is assumed that resolution is formatted as '\d+p'.
                        if int(stream[2][0:-1]) > int(selected[2][0:-1]):
                            selected = stream

        return selected

    def youtube_download(self, context, itag, output_path, filename):
        """
        This method downloads a YouTube stream.

        :param YouTube context: An instance of the pytube.YouTube class.
        :param str itag: The YouTube stream's itag.
        :param str output_path: The download directory.
        :param str filename: The download filename.
        :rtype: None
        """

        path = context.streams.get_by_itag(itag) \
            .download(output_path=output_path, filename=filename)

        return path

    def insert_youtube_url(self, url, desc=None):
        """
        This method inserts a YouTube video into the video collection.

        :param str url: The URL of the YouTube video.
        :param str desc: An optional description of the video.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        try:
            context = self.youtube_context(url)
        except pytube.exceptions.VideoUnavailable:
            raise CommandLineRouteHandlerError(
                f'A VideoUnavailable exception was raised and caught for '
                f'{url}')

        streams = self.youtube_streams(context)
        stream = self.youtube_select(streams)

        try:
            path = self.youtube_download(context, stream[0], VideoDir.path(),
                                         self.uuid())
        except urllib.error.HTTPError as e:  # noqa
            raise CommandLineRouteHandlerError(
                f'An HTTPError exception was raised and caught for {url} '
                f'with HTTP status code {e.code}')

        filename = os.path.basename(path)

        video_id = VideoModel().insert(url, filename, desc)

        debug(f'video_id={video_id}, uri={url}, filename={filename}, '
              f'description={desc}', 3)

    def insert_youtube(self, path, opts={}):
        """
        This method determines the action to take on the path. If the path is a
        path to a file, it will parase the file expecting it to contain URLs to
        YouTube videos separated by newlines. If the path is a URL it will
        attempt to download the video directly.

        :param str path: The path to a local file containing YouTube URLs or a
            YouTube URL directly.
        :param dict opts: The optional dict of options.
        :rtype: None
        """

        urls = []
        descs = []

        if os.path.exists(path):
            with open(path, 'r') as file_:
                lines = [line.strip().split(',', maxsplit=1) for line in file_]
                urls = [line[0].strip() for line in lines]
                descs = [line[1].strip() if len(line) >= 2 else None for line
                         in lines]
        else:
            if 'file' in opts and os.path.isfile(opts['file']):
                self.insert_file(opts['file'], opts)
            else:
                urls.append(path)
                descs.append(opts.get('description', None))

        for url_, desc_ in zip(urls, descs):
            self.insert_youtube_url(url_, desc_)

    def vimeo_context(self, url):
        """
        This method returns an instance of the
        vimeo_dl.vimeo_internal.InternVimeo class.

        :param str url: The URL to a Vimeo video.
        :rtype: vimeo_dl.vimeo_internal.InternVimeo
        """

        return vimeo.new(url)

    def vimeo_title(self, video):
        """
        This method retrieves the title of the Vimeo video.

        :param vimeo_dl.vimeo_internal.InternVimeo video: The Vimeo video.
        :rtype: str
        """

        return video.title

    def vimeo_stream(self, video, quality='hq'):
        """
        This method selects the given video stream that matches the specified
        quality. Quality can be:
          - hq: highest quality
          - lq: lowest quality
          - YYYxZZZ: video with the given dimensions
        If a certain quality video can't be found than a
        CommandLineRouteHandlerError is raised.

        :param vimeo_dl.vimeo_internal.InternVimeo video: The Vimeo video.
        :param str quality: The quality of the video stream to download.
        :rtype: vimeo_dl.vimeo_internal.InternStream
        """

        stream = None
        if quality != 'hq' or quality != 'lq':
            for s in video.streams:
                info = str(s).split('@')[1]
                if info == quality:
                    stream = s
                    break
    
            if stream is None:
                options = ', '.join([str(s).split('@')[1]
                                     for s in video.streams])
                raise CommandLineRouteHandlerError(
                    f'A video with the dimensions "{quality}" could not be '
                    f'found. Available quality options: {options}.'
                )
    
        if quality == 'lq':
            stream = video.streams[-1]
        elif stream is None:
            stream = video.streams[0]
        
        return stream
    
    def vimeo_stream_download(self, stream, output_path, filename):
        """
        This method downloads the Vimeo video stream to the video directory
        with the given filename.

        :param stream: The Vimeo video stream.
        :param str filename: The filename for the downloaded video.
        :rtype: None
        """

        stream.download(filepath=os.path.join(output_path, filename),
                        quiet=False)
                    
    def insert_vimeo_url(self, url, quality='hq', desc=None):
        """
        This method inserts a Vimeo video into the video collection.

        :param str url: The URL of the Vimeo video.
        :param str desc: An optional description of the video.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        try:
            video = self.vimeo_context(url)
        except KeyError:
            raise CommandLineRouteHandlerError(
                f'A KeyError exception was raised and caught for '
                f'{url}')
        
        if desc is None:
            desc = self.vimeo_title(video)
        
        stream = self.vimeo_stream(video, quality)

        filename = f'{self.uuid()}.mp4'
        self.vimeo_stream_download(stream, VideoDir.path(), filename)

        video_id = VideoModel().insert(url, filename, desc)

        debug(f'video_id={video_id}, uri={url}, filename={filename}, '
              f'description={desc}', 3)

    def insert_vimeo(self, path, opts={}):
        """
        This method determines the action to take on the path. If the path is a
        path to a file, it will parase the file expecting it to contain URLs to
        Vimeo videos separated by newlines. If the path is a URL it will
        attempt to download the video directly.

        :param str path: The path to a local file containing Vimeo URLs or a
            Vimeo URL directly.
        :param dict opts: The optional dict of options.
        :rtype: None
        """

        urls = []
        descs = []
        quality = opts.get('quality', 'hq')

        if os.path.exists(path):
            with open(path, 'r') as file_:
                lines = [line.strip().split(',', maxsplit=1) for line in file_]
                urls = [line[0].strip() for line in lines]
                descs = [line[1].strip() if len(line) >= 2 else None for line
                         in lines]
        else:
            if 'file' in opts and os.path.isfile(opts['file']):
                self.insert_file(opts['file'], opts)
            else:
                urls.append(path)
                descs.append(opts.get('description', None))

        for url_, desc_ in zip(urls, descs):
            self.insert_vimeo_url(url_, quality, desc_)

    def insert_image(self, image_path, opts):
        """
        This method inserts a video from an image.

        :param str image_path: The path to the image.
        :param dict opts: The dict of options.
        :rtype: None
        """

        with tempdir() as tempdir_:
            video_path = os.path.join(tempdir_, 'video.mp4')

            ret = create_one_video_file_from_one_image_file(
                image_path, video_path,
                frame_count=int(opts.get('frame-count', '1')))
            if ret is False:
                raise CommandLineRouteHandlerError(
                    'An error occured while attempting to create one video '
                    'file from one image file')

            self.insert_file(video_path, opts)

    def list(self):
        """
        This method lists videos in the video collection.

        :rtype: None
        """

        result = VideoModel().list()

        debug(f'{len(result)} results', 3)
        debug('id | uri | filename | description', 3)
        debug('---------------------------------', 3)

        for r in result:
            debug(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}', 3)

    def select_extract(self, video_ids, opts={}):
        """
        This method extracts frames and thumbnails from a video to a frame set.

        :param list(int) video_ids: The video IDs.
        :param dict opts: The optional dict of options.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        video_model = VideoModel()

        for video_id in video_ids:
            result = video_model.select(video_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Video with ID {video_id:08d} not found')

        plugin = Plugin.get('video_select_extract', 'default')

        for video_id in video_ids:
            frame_set_id = plugin().video_select_extract(
                               video_id,
                               sub_sample=int(opts.get('sub-sample', 1)),
                               max_sample=int(opts.get('max-sample', 0)))

            debug(f'frame_set_id={frame_set_id}, video_id={video_id}', 3)

    def delete(self, video_ids):
        """
        This method deletes a video from the video collection.

        :param list(ints) video_ids: The video IDs.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        video_model = VideoModel()

        for video_id in video_ids:
            result = video_model.select(video_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Video with ID {video_id:08d} not found')

        for video_id in video_ids:
            result = video_model.select(video_id)

            path = VideoFile.path(result[2])

            video_model.delete(video_id)

            os.remove(path)

            debug(f'Video {video_id} was successfully deleted', 3)

    def select_deploy(self, video_id, name, opts):
        """
        This method deploys a video via a plugin.

        :param int video_id: The video ID.
        :param str name: The plugin name.
        :param opts dict: The dict of options.
        :rtype: None
        """

        video_model = VideoModel()

        result = video_model.select(video_id)
        if result is None:
            raise CommandLineRouteHandlerError(
                f'Video with ID {video_id:08d} not found')

        plugin = Plugin.get('video_select_deploy', name)
        if plugin is None:
            raise CommandLineRouteHandlerError(
                f"'{name}' is not a valid frame set extraction plugin name")

        plugin().video_select_deploy(video_id, opts)

        debug('success', 3)

    def select_detect(self, video_id, model_name, opts):
        """
        This method runs a deepfake detection model over a video.

        :param int video_id: The video ID.
        :param str model_name: The name of the detection model to run.
        :param opts dict: The dict of options.
        """

        video_model = VideoModel()

        result = video_model.select(video_id)
        if result is None:
            raise CommandLineRouteHandlerError(
                f'Video with ID {video_id:08d} not found')

        plugin = Plugin.get('video_select_detect', model_name)
        if plugin is None:
            raise CommandLineRouteHandlerError(
                f"'{model_name}' is not a valid video select detect plugin name")

        video_path = VideoFile.path(result[2])
        plugin().video_select_detect(video_path, **opts)

    def usage(self):
        """
        This method prints usage.

        :rtype: None
        """

        path = os.path.join(
                   os.path.dirname(os.path.realpath(__file__)),
                   'video_command_line_route_handler_usage.txt')

        with open(path, 'r') as file_:
            usage = file_.read()

        usage = usage.strip()

        debug(usage, 3)

    def handle(self, args, opts):
        """
        This method handles command line arguments for the video collection.

        :param list(str) args: The list of command line arguments.
        :param dict opts: The dict of options.
        :rtype: None
        """

        if args[1] == 'insert' and args[3] == 'file':
            self.insert_file(args[4], opts)
        elif args[1] == 'insert' and args[3] == 'youtube':
            self.insert_youtube(args[4], opts)
        elif args[1] == 'insert' and args[3] == 'vimeo':
            self.insert_vimeo(args[4], opts)
        elif args[1] == 'insert' and args[3] == 'image':
            self.insert_image(args[4], opts)
        elif args[1] == 'list':
            self.list()
        elif args[1] == 'select' and args[4] == 'extract':
            self.select_extract(parse_range(args[3]), opts)
        elif args[1] == 'delete':
            self.delete(parse_range(args[3]))
        elif args[1] == 'select' and args[4] == 'deploy':
            self.select_deploy(int(args[3]), args[5], opts)
        elif args[1] == 'select' and args[4] == 'detect':
            self.select_detect(int(args[3]), args[5], opts)
        elif args[1] == 'usage':
            self.usage()
