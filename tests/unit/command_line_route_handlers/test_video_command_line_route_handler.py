from io import StringIO
import mock
import os
import re
import shutil
import sys
import textwrap
import unittest
import urllib
from uuid import UUID

import cv2
import pytube

from deepstar.command_line_route_handlers.video_command_line_route_handler \
    import VideoCommandLineRouteHandler
from deepstar.filesystem.frame_file import FrameFile
from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir
from deepstar.filesystem.video_file import VideoFile
from deepstar.models.frame_model import FrameModel
from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.video_model import VideoModel
from deepstar.plugins.plugin import Plugin
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError

from .. import deepstar_path


class TestVideoCommandLineRouteHandler(unittest.TestCase):
    """
    This class tests the VideoCommandLineRouteHandler class.
    """

    def test_insert_file(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def uuid(self):
                    return '12345678-1234-1234-1234-123456789012'

            args = ['main.py', 'insert', 'videos', 'file', video_0001]
            opts = {}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = 'video_id=1, uri=' + video_0001 + ', filename=12345678-1234-1234-1234-123456789012.mp4, description=None'  # noqa

            self.assertEqual(actual, expected)

            # db
            result = VideoModel().select(1)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], 1)
            self.assertEqual(result[1], video_0001)
            UUID(result[2].rstrip('.mp4'), version=4)
            self.assertEqual(result[3], None)

            # files
            self.assertTrue(os.path.isfile(VideoFile.path(result[2])))

    def test_insert_file_description(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def uuid(self):
                    return '12345678-1234-1234-1234-123456789012'

            args = ['main.py', 'insert', 'videos', 'file', video_0001]
            opts = {'description': 'test'}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = 'video_id=1, uri=' + video_0001 + ', filename=12345678-1234-1234-1234-123456789012.mp4, description=test'  # noqa

            self.assertEqual(actual, expected)

            # db
            result = VideoModel().select(1)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], 1)
            self.assertEqual(result[1], video_0001)
            UUID(result[2].rstrip('.mp4'), version=4)
            self.assertEqual(result[3], 'test')

    def test_insert_file_fails_to_open_a_video_file(self):
        with deepstar_path():
            args = ['main.py', 'insert', 'videos', 'file', 'test']
            opts = {}

            route_handler = VideoCommandLineRouteHandler()

            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                with self.assertRaises(CommandLineRouteHandlerError):
                    try:
                        route_handler.handle(args, opts)
                    except CommandLineRouteHandlerError as e:
                        self.assertEqual(e.message, 'File test not found')

                        raise e

    def test_uuid(self):
        UUID(VideoCommandLineRouteHandler().uuid(), version=4)

    def test_insert_youtube_file(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def __init__(self):
                    self._uuids = [
                        '32345678-1234-1234-1234-123456789012',
                        '22345678-1234-1234-1234-123456789012',
                        '12345678-1234-1234-1234-123456789012'
                    ]

                def youtube_context(self, url):
                    return None

                def youtube_streams(self, context):
                    return [
                        ['22', 'video/mp4', '720p']
                    ]

                def uuid(self):
                    return self._uuids.pop()

                def youtube_download(self, context, stream, output_path, filename):  # noqa
                    filename = filename + '.mp4'

                    shutil.copyfile(video_0001, output_path + '/' + filename)

                    return filename

            path = os.environ['DEEPSTAR_PATH'] + '/test.txt'

            with open(path, 'w') as file_:
                file_.write('https://www.youtube.com/watch?v=test1\n')
                file_.write('https://www.youtube.com/watch?v=test2\n')
                file_.write('https://www.youtube.com/watch?v=test3\n')

            args = ['main.py', 'insert', 'videos', 'youtube', path]
            opts = {}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = \
                'video_id=1, uri=https://www.youtube.com/watch?v=test1, ' \
                'filename=12345678-1234-1234-1234-123456789012.mp4, ' \
                'description=None\n' \
                'video_id=2, uri=https://www.youtube.com/watch?v=test2, ' \
                'filename=22345678-1234-1234-1234-123456789012.mp4, ' \
                'description=None\n' \
                'video_id=3, uri=https://www.youtube.com/watch?v=test3, ' \
                'filename=32345678-1234-1234-1234-123456789012.mp4, ' \
                'description=None'

            self.assertEqual(actual, expected)

            # db + files
            result = VideoModel().select(1)
            self.assertEqual(result[0], 1)
            self.assertEqual(result[1], 'https://www.youtube.com/watch?v=test1')  # noqa
            UUID(result[2].rstrip('.mp4'), version=4)
            self.assertTrue(os.path.isfile(VideoFile.path(result[2])))
            self.assertEqual(result[3], None)

            result = VideoModel().select(2)
            self.assertEqual(result[0], 2)
            self.assertEqual(result[1], 'https://www.youtube.com/watch?v=test2')  # noqa
            UUID(result[2].rstrip('.mp4'), version=4)
            self.assertTrue(os.path.isfile(VideoFile.path(result[2])))
            self.assertEqual(result[3], None)

            result = VideoModel().select(3)
            self.assertEqual(result[0], 3)
            self.assertEqual(result[1], 'https://www.youtube.com/watch?v=test3')  # noqa
            UUID(result[2].rstrip('.mp4'), version=4)
            self.assertTrue(os.path.isfile(VideoFile.path(result[2])))
            self.assertEqual(result[3], None)

    def test_insert_youtube_file_description(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def youtube_context(self, url):
                    return None

                def youtube_streams(self, context):
                    return [
                        ['22', 'video/mp4', '720p']
                    ]

                def uuid(self):
                    return '12345678-1234-1234-1234-123456789012'

                def youtube_download(self, context, stream, output_path, filename):  # noqa
                    filename = filename + '.mp4'

                    shutil.copyfile(video_0001, output_path + '/' + filename)

                    return filename

            path = os.environ['DEEPSTAR_PATH'] + '/test.txt'

            with open(path, 'w') as file_:
                file_.write('https://www.youtube.com/watch?v=test1, test')

            args = ['main.py', 'insert', 'videos', 'youtube', path]
            opts = {}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = \
                'video_id=1, uri=https://www.youtube.com/watch?v=test1, ' \
                'filename=12345678-1234-1234-1234-123456789012.mp4, ' \
                'description=test' \

            self.assertEqual(actual, expected)

            # db + files
            result = VideoModel().select(1)
            self.assertEqual(result[0], 1)
            self.assertEqual(result[1], 'https://www.youtube.com/watch?v=test1')  # noqa
            UUID(result[2].rstrip('.mp4'), version=4)
            self.assertTrue(os.path.isfile(VideoFile.path(result[2])))
            self.assertEqual(result[3], 'test')

    def test_insert_youtube_url(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def youtube_context(self, url):
                    return None

                def youtube_streams(self, context):
                    return [
                        ['22', 'video/mp4', '720p']
                    ]

                def uuid(self):
                    return '12345678-1234-1234-1234-123456789012'

                def youtube_download(self, context, stream, output_path, filename):  # noqa
                    filename = filename + '.mp4'

                    shutil.copyfile(video_0001, output_path + '/' + filename)

                    return filename

            args = ['main.py', 'insert', 'videos', 'youtube', 'https://www.youtube.com/watch?v=test']  # noqa
            opts = {}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'video_id=1, uri=https://www.youtube.com/watch?v=test, filename=12345678-1234-1234-1234-123456789012.mp4, description=None')  # noqa

            # db + files
            result = VideoModel().select(1)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], 1)
            self.assertEqual(result[1], 'https://www.youtube.com/watch?v=test')  # noqa
            UUID(result[2].rstrip('.mp4'), version=4)
            self.assertTrue(os.path.isfile(VideoFile.path(result[2])))
            self.assertEqual(result[3], None)

    def test_insert_youtube_url_description(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def youtube_context(self, url):
                    return None

                def youtube_streams(self, context):
                    return [
                        ['22', 'video/mp4', '720p']
                    ]

                def uuid(self):
                    return '12345678-1234-1234-1234-123456789012'

                def youtube_download(self, context, stream, output_path, filename):  # noqa
                    filename = filename + '.mp4'

                    shutil.copyfile(video_0001, output_path + '/' + filename)

                    return filename

            args = ['main.py', 'insert', 'videos', 'youtube', 'https://www.youtube.com/watch?v=test']  # noqa
            opts = {'description': 'test'}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'video_id=1, uri=https://www.youtube.com/watch?v=test, filename=12345678-1234-1234-1234-123456789012.mp4, description=test')  # noqa

            # db + files
            result = VideoModel().select(1)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], 1)
            self.assertEqual(result[1], 'https://www.youtube.com/watch?v=test')  # noqa
            UUID(result[2].rstrip('.mp4'), version=4)
            self.assertTrue(os.path.isfile(VideoFile.path(result[2])))
            self.assertEqual(result[3], 'test')

    def test_insert_youtube_url_file(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def uuid(self):
                    return '12345678-1234-1234-1234-123456789012'

            args = ['main.py', 'insert', 'videos', 'youtube', 'https://www.youtube.com/watch?v=test']  # noqa
            opts = {'file': video_0001}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertIsNotNone(re.match('^video_id=1, uri=.*video_0001.mp4, filename=12345678-1234-1234-1234-123456789012.mp4, description=None$', actual))  # noqa

            # db + files
            result = VideoModel().select(1)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], 1)
            self.assertIsNotNone(re.match('^.*video_0001.mp4', result[1]))
            UUID(result[2].rstrip('.mp4'), version=4)
            self.assertTrue(os.path.isfile(VideoFile.path(result[2])))
            self.assertEqual(result[3], None)

    def test_insert_youtube_fails_with_video_unavailable(self):
        with deepstar_path():
            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def youtube_context(self, url):
                    raise pytube.exceptions.VideoUnavailable()

                def youtube_streams(self, context):
                    return [
                        ['22', 'video/mp4', '720p']
                    ]

                def youtube_download(self, context, stream, output_path, filename):  # noqa
                    pass

            args = ['main.py', 'insert', 'videos', 'youtube', 'https://www.youtube.com/watch?v=test']  # noqa
            opts = {}

            route_handler = TestVideoCommandLineRouteHandler_()

            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                with self.assertRaises(CommandLineRouteHandlerError):
                    try:
                        route_handler.handle(args, opts)
                    except CommandLineRouteHandlerError as e:
                        self.assertEqual(e.message, 'A VideoUnavailable exception was raised and caught for https://www.youtube.com/watch?v=test')  # noqa

                        raise e

    def test_insert_youtube_fails_with_http_error(self):
        with deepstar_path():
            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def youtube_context(self, url):
                    return None

                def youtube_streams(self, context):
                    return [
                        ['22', 'video/mp4', '720p']
                    ]

                def youtube_download(self, context, stream, output_path, filename):  # noqa
                    # TypeError: __init__() missing 5 required positional arguments: 'url', 'code', 'msg', 'hdrs', and 'fp'  # noqa
                    raise urllib.error.HTTPError(url='test', code=123, msg='test', hdrs={'test': 'test'}, fp=None)  # noqa

            args = ['main.py', 'insert', 'videos', 'youtube', 'https://www.youtube.com/watch?v=test']  # noqa
            opts = {}

            route_handler = TestVideoCommandLineRouteHandler_()

            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                with self.assertRaises(CommandLineRouteHandlerError):
                    try:
                        route_handler.handle(args, opts)
                    except CommandLineRouteHandlerError as e:
                        self.assertEqual(e.message, 'An HTTPError exception was raised and caught for https://www.youtube.com/watch?v=test with HTTP status code 123')  # noqa

                        raise e

    def test_insert_vimeo_url(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def vimeo_context(self, url):
                    return None

                def vimeo_title(self, video):
                    return 'Unittest video'
                
                def vimeo_stream(self, video, quality):
                    return None

                def uuid(self):
                    return '12345678-1234-1234-1234-123456789012'

                def vimeo_stream_download(self, stream, output_path, filename):
                    shutil.copyfile(video_0001,
                                    os.path.join(output_path, filename))

            args = ['main.py', 'insert', 'videos', 'vimeo', 'https://vimeo.com/test']  # noqa
            opts = {}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'video_id=1, uri=https://vimeo.com/test, filename=12345678-1234-1234-1234-123456789012.mp4, description=Unittest video')  # noqa

            # db + files
            result = VideoModel().select(1)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], 1)
            self.assertEqual(result[1], 'https://vimeo.com/test')  # noqa
            UUID(result[2].rstrip('.mp4'), version=4)
            self.assertTrue(os.path.isfile(VideoFile.path(result[2])))
            self.assertEqual(result[3], 'Unittest video')

    def test_insert_vimeo(self):
        with deepstar_path():
            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def insert_vimeo_url(self, url, quality, desc):
                    print(f'uri={url}, quality={quality}, description={desc}')

            args = ['main.py', 'insert', 'videos', 'vimeo', 'https://vimeo.com/test']  # noqa
            opts = {}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__
            
            # stdout
            self.assertEqual(actual, 'uri=https://vimeo.com/test, quality=hq, description=None')  # noqa

    def test_insert_vimeo_quality(self):
        with deepstar_path():
            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def insert_vimeo_url(self, url, quality, desc):
                    print(f'uri={url}, quality={quality}, description={desc}')

            args = ['main.py', 'insert', 'videos', 'vimeo', 'https://vimeo.com/test']  # noqa
            opts = {'quality': '640x360'}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__
            
            # stdout
            self.assertEqual(actual, 'uri=https://vimeo.com/test, quality=640x360, description=None')  # noqa

    def test_insert_vimeo_description(self):
        with deepstar_path():
            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def insert_vimeo_url(self, url, quality, desc):
                    print(f'uri={url}, quality={quality}, description={desc}')

            args = ['main.py', 'insert', 'videos', 'vimeo', 'https://vimeo.com/test']  # noqa
            opts = {'description': 'Unittest'}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__
            
            # stdout
            self.assertEqual(actual, 'uri=https://vimeo.com/test, quality=hq, description=Unittest')  # noqa
                    
    def test_insert_vimeo_file(self):
        with deepstar_path():
            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def insert_vimeo_url(self, url, quality, desc):
                    print(f'uri={url}, quality={quality}, description={desc}')

            path = os.environ['DEEPSTAR_PATH'] + '/test.txt'

            with open(path, 'w') as file_:
                file_.write('https://vimeo.com/test1\n')
                file_.write('https://vimeo.com/test2\n')
                file_.write('https://vimeo.com/test3\n')

            args = ['main.py', 'insert', 'videos', 'vimeo', path]
            opts = {}

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__
            
            # stdout
            expected = 'uri=https://vimeo.com/test1, quality=hq, description=None\n' + \
                'uri=https://vimeo.com/test2, quality=hq, description=None\n' + \
                'uri=https://vimeo.com/test3, quality=hq, description=None'
            self.assertEqual(actual, expected)

    def test_insert_image(self):
        with deepstar_path():
            image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0001.jpg'  # noqa

            args = ['main.py', 'insert', 'videos', 'image', image_0001]
            opts = {}

            class TestVideoCommandLineRouteHandler_(VideoCommandLineRouteHandler):  # noqa
                def uuid(self):
                    return '12345678-1234-1234-1234-123456789012'

            route_handler = TestVideoCommandLineRouteHandler_()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertIsNotNone(re.match('^video_id=1, uri=.*video.mp4, filename=12345678-1234-1234-1234-123456789012.mp4, description=None$', actual))  # noqa

            # db
            result = VideoModel().select(1)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], 1)
            self.assertIsNotNone(re.match('^.*video.mp4$', result[1]))
            self.assertEqual(result[2], '12345678-1234-1234-1234-123456789012.mp4')  # noqa
            self.assertEqual(result[3], None)

            # files
            video_path = VideoFile.path(result[2])

            vc = cv2.VideoCapture(video_path)

            try:
                self.assertTrue(vc.isOpened())
                self.assertEqual(vc.get(cv2.CAP_PROP_FRAME_COUNT), 1)
            finally:
                vc.release()

    def test_insert_image_description(self):
        with deepstar_path():
            image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0001.jpg'  # noqa

            args = ['main.py', 'insert', 'videos', 'image', image_0001]
            opts = {'description': 'test'}

            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                VideoCommandLineRouteHandler().handle(args, opts)

            # db
            self.assertEqual(VideoModel().select(1)[3], 'test')

    def test_insert_image_frame_count(self):
        with deepstar_path():
            image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0001.jpg'  # noqa

            args = ['main.py', 'insert', 'videos', 'image', image_0001]
            opts = {'frame-count': '5'}

            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                VideoCommandLineRouteHandler().handle(args, opts)

            # files
            video_path = VideoFile.path(VideoModel().select(1)[2])

            vc = cv2.VideoCapture(video_path)

            try:
                self.assertTrue(vc.isOpened())
                self.assertEqual(vc.get(cv2.CAP_PROP_FRAME_COUNT), 5)
            finally:
                vc.release()

    def test_insert_image_fails_to_open_image(self):
        with deepstar_path():
            args = ['main.py', 'insert', 'videos', 'image', 'test']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    VideoCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'An error occured while attempting to create one video file from one image file')  # noqa

                    raise e

    def test_list(self):
        with deepstar_path():
            video_model = VideoModel()
            video_model.insert('test1', 'test2')
            video_model.insert('test3', 'test4')
            video_model.insert('test5', 'test6')

            args = ['main.py', 'list', 'videos']
            opts = {}

            route_handler = VideoCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = textwrap.dedent('''
            3 results
            id | uri | filename | description
            ---------------------------------
            1 | test1 | test2 | None
            2 | test3 | test4 | None
            3 | test5 | test6 | None''').strip()

            self.assertEqual(actual, expected)

    def test_select_curate(self):
        pass

    def test_select_extract_one(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            args = ['main.py', 'select', 'videos', '1', 'extract']
            opts = {}

            route_handler = VideoCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'frame_set_id=1, video_id=1')

            # db
            result = FrameSetModel().select(1)
            self.assertEqual(result, (1, 1))

            result = FrameModel().list(1)
            self.assertEqual(len(result), 5)
            self.assertEqual(result[0], (1, 1, 0))
            self.assertEqual(result[1], (2, 1, 0))
            self.assertEqual(result[2], (3, 1, 0))
            self.assertEqual(result[3], (4, 1, 0))
            self.assertEqual(result[4], (5, 1, 0))

            # files
            p1 = FrameSetSubDir.path(1)

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 3, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 4, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 5, 'jpg')))

            # thumbnails
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 3, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 4, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 5, 'jpg', '192x192')))  # noqa

    def test_select_extract_many(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))
            shutil.copyfile(video_0001, VideoFile.path('video_0002.mp4'))
            shutil.copyfile(video_0001, VideoFile.path('video_0003.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')
            VideoModel().insert('test', 'video_0002.mp4')
            VideoModel().insert('test', 'video_0003.mp4')

            args = ['main.py', 'select', 'videos', '1-2,3', 'extract']
            opts = {}

            route_handler = VideoCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = textwrap.dedent('''
            frame_set_id=1, video_id=1
            frame_set_id=2, video_id=2
            frame_set_id=3, video_id=3
            ''').strip()

            self.assertEqual(actual, expected)

    def test_select_extract_sub_sample(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            args = ['main.py', 'select', 'videos', '1', 'extract']
            opts = {'sub-sample': '2'}

            route_handler = VideoCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'frame_set_id=1, video_id=1')

            # db
            result = FrameModel().list(1)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0], (1, 1, 0))
            self.assertEqual(result[1], (2, 1, 0))
            self.assertEqual(result[2], (3, 1, 0))

            # files
            p1 = FrameSetSubDir.path(1)

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 3, 'jpg')))

            # thumbnails
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 3, 'jpg', '192x192')))  # noqa

    def test_select_extract_max_sample(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            args = ['main.py', 'select', 'videos', '1', 'extract']
            opts = {'max-sample': '2'}

            route_handler = VideoCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'frame_set_id=1, video_id=1')

            # db
            result = FrameModel().list(1)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], (1, 1, 0))
            self.assertEqual(result[1], (2, 1, 0))

            # files
            p1 = FrameSetSubDir.path(1)

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg')))

            # thumbnails
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg', '192x192')))  # noqa

    def test_select_extract_fails_to_select_a_video(self):
        with deepstar_path():
            args = ['main.py', 'select', 'videos', '1', 'extract']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    VideoCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Video with ID 00000001 not found')  # noqa

                    raise e

    def test_select_extract_fails_to_open_a_video_file(self):
        with deepstar_path():
            VideoModel().insert('test', 'test')

            args = ['main.py', 'select', 'videos', '1', 'extract']
            opts = {}

            route_handler = VideoCommandLineRouteHandler()

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    route_handler.handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, f'OpenCV VideoCapture isOpened returned false for {VideoFile.path("test")}')  # noqa

                    raise e

    def test_select_deploy(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            class TestPlugin:
                def video_select_deploy(self, video_id, opts):
                    pass

            args = ['main.py', 'select', 'videos', '1', 'deploy', 'test']
            opts = {}

            route_handler = VideoCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(Plugin._map, {'video_select_deploy': {'test': TestPlugin}}):  # noqa
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'success')

    def test_select_deploy_fails_to_select_a_video(self):
        with deepstar_path():
            args = ['main.py', 'select', 'videos', '1', 'deploy', 'test']
            opts = {}

            route_handler = VideoCommandLineRouteHandler()

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    route_handler.handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, f'Video with ID 00000001 not found')  # noqa

                    raise e

    def test_select_deploy_fails_to_get_a_plugin(self):
        with deepstar_path():
            VideoModel().insert('test', 'test')

            args = ['main.py', 'select', 'videos', '1', 'deploy', 'test']
            opts = {}

            route_handler = VideoCommandLineRouteHandler()

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    route_handler.handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, "'test' is not a valid frame set extraction plugin name")  # noqa

                    raise e

    def test_delete_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

            video_model = VideoModel()

            old = video_model.select(1)
            self.assertIsNotNone(old)

            args = ['main.py', 'delete', 'videos', '1']
            opts = {}

            route_handler = VideoCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'Video 1 was successfully deleted')

            # db + files
            new = video_model.select(1)
            self.assertIsNone(new)
            self.assertFalse(os.path.exists(VideoFile.path(old[2])))

    def test_delete_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)

            args = ['main.py', 'delete', 'videos', '1-2,3']
            opts = {}

            route_handler = VideoCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = textwrap.dedent('''
            Video 1 was successfully deleted
            Video 2 was successfully deleted
            Video 3 was successfully deleted''').strip()

            self.assertEqual(actual, expected)

    def test_delete_fails_to_select_a_video(self):
        with deepstar_path():
            args = ['main.py', 'delete', 'videos', '1']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    VideoCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Video with ID 00000001 not found')  # noqa

                    raise e

    def test_usage(self):
        with deepstar_path():
            route_handler = VideoCommandLineRouteHandler()

            args = ['main.py', 'usage', 'videos']
            opts = {}

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            self.assertTrue('Usage - Videos' in actual)
