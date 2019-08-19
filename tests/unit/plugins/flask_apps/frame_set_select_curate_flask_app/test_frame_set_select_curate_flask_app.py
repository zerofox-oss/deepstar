import json
import mock
import os
import unittest

import cv2
import numpy as np

from deepstar.plugins.flask_apps \
    .frame_set_select_curate_flask_app.frame_set_select_curate_flask_app \
    import FrameSetSelectCurateFlaskApp
from deepstar.command_line_route_handlers.video_command_line_route_handler \
    import VideoCommandLineRouteHandler

from .... import deepstar_path


class TestFrameSetSelectCurateFlaskApp(unittest.TestCase):
    """
    This class tests the FrameSetSelectCurateFlaskApp class.
    """

    def setUp_(self):
        with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
            route_handler = VideoCommandLineRouteHandler()

            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../../../support/video_0001.mp4'  # noqa

            route_handler.insert_file(video_0001)

            route_handler.select_extract([1])

    def test_static(self):
        with deepstar_path():
            self.setUp_()

            api = FrameSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/static/img/checkmark.png')
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(cv2.imdecode(np.fromstring(response.get_data(), dtype=np.uint8), cv2.IMREAD_UNCHANGED), np.ndarray)  # noqa

            response = api.get('/static/img/xmark.png')
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(cv2.imdecode(np.fromstring(response.get_data(), dtype=np.uint8), cv2.IMREAD_UNCHANGED), np.ndarray)  # noqa

    def test_templates(self):
        with deepstar_path():
            api = FrameSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertTrue('html' in response.get_data().decode('utf-8'))

    def test_frame_collection_list(self):
        with deepstar_path():
            self.setUp_()

            api = FrameSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/frame_sets/1/frames/')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 5)
            self.assertEqual(t[0], [1, 1, 0])
            self.assertEqual(t[1], [2, 1, 0])
            self.assertEqual(t[2], [3, 1, 0])
            self.assertEqual(t[3], [4, 1, 0])
            self.assertEqual(t[4], [5, 1, 0])

            response = api.get('/frame_sets/1/frames/?offset=0&length=5')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 5)
            self.assertEqual(t[0], [1, 1, 0])
            self.assertEqual(t[1], [2, 1, 0])
            self.assertEqual(t[2], [3, 1, 0])
            self.assertEqual(t[3], [4, 1, 0])
            self.assertEqual(t[4], [5, 1, 0])

            response = api.get('/frame_sets/1/frames/?offset=1')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 4)
            self.assertEqual(t[0], [2, 1, 0])
            self.assertEqual(t[1], [3, 1, 0])
            self.assertEqual(t[2], [4, 1, 0])
            self.assertEqual(t[3], [5, 1, 0])

            response = api.get('/frame_sets/1/frames/?length=3')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 3)
            self.assertEqual(t[0], [1, 1, 0])
            self.assertEqual(t[1], [2, 1, 0])
            self.assertEqual(t[2], [3, 1, 0])

            response = api.get('/frame_sets/1/frames/?offset=1&length=3')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 3)
            self.assertEqual(t[0], [2, 1, 0])
            self.assertEqual(t[1], [3, 1, 0])
            self.assertEqual(t[2], [4, 1, 0])

    def test_frame_collection_list_fails_to_list_frame_set(self):
        with deepstar_path():
            self.setUp_()

            api = FrameSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/frame_sets/2/frames/')
            self.assertEqual(response.status_code, 404)

    def test_frame_get(self):
        with deepstar_path():
            self.setUp_()

            api = FrameSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/frame_sets/1/frames/1')
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(cv2.imdecode(np.fromstring(response.get_data(), dtype=np.uint8), cv2.IMREAD_UNCHANGED), np.ndarray)  # noqa

    def test_frame_get_fails_to_select_frame(self):
        with deepstar_path():
            self.setUp_()

            api = FrameSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/frame_sets/1/frames/6')
            self.assertEqual(response.status_code, 404)

    def test_frame_put(self):
        with deepstar_path():
            self.setUp_()

            api = FrameSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/frame_sets/1/frames/?length=1')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 1)
            self.assertEqual(t[0], [1, 1, 0])

            response = api.put('/frame_sets/1/frames/1', data=json.dumps({'rejected': 1}), headers={'Content-Type': 'application/json'})  # noqa
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(t, [1, 1, 1])

            response = api.get('/frame_sets/1/frames/?length=1')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(t[0], [1, 1, 1])

    def test_frame_put_fails_to_update_frame(self):
        with deepstar_path():
            self.setUp_()

            api = FrameSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.put('/frame_sets/1/frames/6', data=json.dumps({'rejected': 1}), headers={'Content-Type': 'application/json'})  # noqa
            self.assertEqual(response.status_code, 404)
