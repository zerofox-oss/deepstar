import json
import mock
import os
import shutil
import unittest

import cv2
import numpy as np

from deepstar.command_line_route_handlers.video_command_line_route_handler \
    import VideoCommandLineRouteHandler
from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.plugins.flask_apps \
    .transform_set_select_curate_flask_app \
    .transform_set_select_curate_flask_app \
    import TransformSetSelectCurateFlaskApp

from .... import deepstar_path


class TestTransformSetSelectCurateFlaskApp(unittest.TestCase):
    """
    This class tests the TransformSetSelectCurateFlaskApp class.
    """

    def mock_transform_set(self):
        image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../../../support/image_0001.jpg'  # noqa

        TransformSetModel().insert('face', 1, None)

        p1 = TransformSetSubDir.path(1)

        os.mkdir(p1)

        transform_model = TransformModel()

        for i in range(0, 5):
            transform_model.insert(1, i + 1, '{}', 0)

            shutil.copy(image_0001, TransformFile.path(p1, i + 1, 'jpg'))

    def setUp_(self):
        with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
            route_handler = VideoCommandLineRouteHandler()

            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../../../support/video_0001.mp4'  # noqa

            route_handler.insert_file(video_0001)

            route_handler.select_extract([1])

            self.mock_transform_set()

    def test_static(self):
        with deepstar_path():
            self.setUp_()

            api = TransformSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/static/img/checkmark.png')
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(cv2.imdecode(np.fromstring(response.get_data(), dtype=np.uint8), cv2.IMREAD_UNCHANGED), np.ndarray)  # noqa

            response = api.get('/static/img/xmark.png')
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(cv2.imdecode(np.fromstring(response.get_data(), dtype=np.uint8), cv2.IMREAD_UNCHANGED), np.ndarray)  # noqa

    def test_templates(self):
        with deepstar_path():
            api = TransformSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertTrue('html' in response.get_data().decode('utf-8'))

    def test_transform_collection_list(self):
        with deepstar_path():
            self.setUp_()

            api = TransformSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/transform_sets/1/transforms/')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 5)
            self.assertEqual(t[0], [1, 1, 1, '{}', 0])
            self.assertEqual(t[1], [2, 1, 2, '{}', 0])
            self.assertEqual(t[2], [3, 1, 3, '{}', 0])
            self.assertEqual(t[3], [4, 1, 4, '{}', 0])
            self.assertEqual(t[4], [5, 1, 5, '{}', 0])

            response = api.get('/transform_sets/1/transforms/?offset=0&length=5')  # noqa
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 5)
            self.assertEqual(t[0], [1, 1, 1, '{}', 0])
            self.assertEqual(t[1], [2, 1, 2, '{}', 0])
            self.assertEqual(t[2], [3, 1, 3, '{}', 0])
            self.assertEqual(t[3], [4, 1, 4, '{}', 0])
            self.assertEqual(t[4], [5, 1, 5, '{}', 0])

            response = api.get('/transform_sets/1/transforms/?offset=1')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 4)
            self.assertEqual(t[0], [2, 1, 2, '{}', 0])
            self.assertEqual(t[1], [3, 1, 3, '{}', 0])
            self.assertEqual(t[2], [4, 1, 4, '{}', 0])
            self.assertEqual(t[3], [5, 1, 5, '{}', 0])

            response = api.get('/transform_sets/1/transforms/?length=3')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 3)
            self.assertEqual(t[0], [1, 1, 1, '{}', 0])
            self.assertEqual(t[1], [2, 1, 2, '{}', 0])
            self.assertEqual(t[2], [3, 1, 3, '{}', 0])

            response = api.get('/transform_sets/1/transforms/?offset=1&length=3')  # noqa
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 3)
            self.assertEqual(t[0], [2, 1, 2, '{}', 0])
            self.assertEqual(t[1], [3, 1, 3, '{}', 0])
            self.assertEqual(t[2], [4, 1, 4, '{}', 0])

    def test_transform_collection_list_fails_to_list_transform_set(self):
        with deepstar_path():
            self.setUp_()

            api = TransformSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/transform_sets/2/transforms/')
            self.assertEqual(response.status_code, 404)

    def test_transform_get(self):
        with deepstar_path():
            self.setUp_()

            api = TransformSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/transform_sets/1/transforms/1')
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(cv2.imdecode(np.fromstring(response.get_data(), dtype=np.uint8), cv2.IMREAD_UNCHANGED), np.ndarray)  # noqa

    def test_transform_get_fails_to_select_transform(self):
        with deepstar_path():
            self.setUp_()

            api = TransformSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/transform_sets/1/transforms/6')
            self.assertEqual(response.status_code, 404)

    def test_transform_put(self):
        with deepstar_path():
            self.setUp_()

            api = TransformSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.get('/transform_sets/1/transforms/?length=1')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(len(t), 1)
            self.assertEqual(t[0], [1, 1, 1, '{}', 0])

            response = api.put('/transform_sets/1/transforms/1', data=json.dumps({'rejected': 1}), headers={'Content-Type': 'application/json'})  # noqa
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(t, [1, 1, 1, '{}', 1])

            response = api.get('/transform_sets/1/transforms/?length=1')
            self.assertEqual(response.status_code, 200)
            t = json.loads(response.get_data().decode('utf-8'))
            self.assertEqual(t[0], [1, 1, 1, '{}', 1])

    def test_transform_put_fails_to_update_transform(self):
        with deepstar_path():
            self.setUp_()

            api = TransformSetSelectCurateFlaskApp(1).api.app.test_client()

            response = api.put('/transform_sets/1/transforms/6', data=json.dumps({'rejected': 1}), headers={'Content-Type': 'application/json'})  # noqa
            self.assertEqual(response.status_code, 404)
