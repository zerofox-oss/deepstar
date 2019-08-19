import unittest

from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.models.video_model import VideoModel

from .. import deepstar_path


class TestTransformSetModel(unittest.TestCase):
    """
    This class tests the TransformSetModel class.
    """

    def test_select(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            FrameSetModel().insert(1)

            transform_set_model = TransformSetModel()
            transform_set_model.insert('test', 1)

            result = transform_set_model.select(1)
            self.assertEqual(result, (1, 'test', 1, None))

    def test_select_fails_to_select_transform_set(self):
        with deepstar_path():
            result = TransformSetModel().select(1)
            self.assertIsNone(result)

    def test_insert(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            FrameSetModel().insert(1)

            transform_set_model = TransformSetModel()
            transform_set_id = transform_set_model.insert('test', 1)
            self.assertEqual(transform_set_id, 1)

            result = transform_set_model.select(1)
            self.assertEqual(result, (1, 'test', 1, None))

    def test_list(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            FrameSetModel().insert(1)

            transform_set_model = TransformSetModel()
            transform_set_model.insert('test', 1)
            transform_set_model.insert('test', 1)
            transform_set_model.insert('test', 1)

            result = transform_set_model.list()
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0], (1, 'test', 1, None))
            self.assertEqual(result[1], (2, 'test', 1, None))
            self.assertEqual(result[2], (3, 'test', 1, None))

    def test_delete(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            FrameSetModel().insert(1)

            transform_set_model = TransformSetModel()
            transform_set_model.insert('test', 1)
            result = transform_set_model.select(1)
            self.assertEqual(result, (1, 'test', 1, None))
            result = transform_set_model.delete(1)
            self.assertTrue(result)
            result = transform_set_model.select(1)
            self.assertIsNone(result)

    def test_delete_fails_to_delete_transform_set(self):
        with deepstar_path():
            result = TransformSetModel().delete(1)
            self.assertFalse(result)
