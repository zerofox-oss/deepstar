import unittest

from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.video_model import VideoModel

from .. import deepstar_path


class TestFrameSetModel(unittest.TestCase):
    """
    This class tests the FrameSetModel class.
    """

    def test_select(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            frame_set_model = FrameSetModel()
            frame_set_model.insert(1)

            result = frame_set_model.select(1)
            self.assertEqual(result, (1, 1))

    def test_select_fails_to_select_frame_set(self):
        with deepstar_path():
            result = FrameSetModel().select(1)
            self.assertIsNone(result)

    def test_insert(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            frame_set_model = FrameSetModel()
            frame_set_id = frame_set_model.insert(1)
            self.assertEqual(frame_set_id, 1)

            result = frame_set_model.select(1)
            self.assertEqual(result, (1, 1))

    def test_list(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            frame_set_model = FrameSetModel()
            frame_set_model.insert(1)
            frame_set_model.insert(1)
            frame_set_model.insert(1)

            result = frame_set_model.list()
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0], (1, 1))
            self.assertEqual(result[1], (2, 1))
            self.assertEqual(result[2], (3, 1))

    def test_delete(self):
        with deepstar_path():
            frame_set_model = FrameSetModel()
            frame_set_model.insert(1)
            result = frame_set_model.select(1)
            self.assertEqual(result, (1, 1))
            result = frame_set_model.delete(1)
            self.assertTrue(result)
            result = frame_set_model.select(1)
            self.assertIsNone(result)

    def test_delete_fails_to_delete_frame_set(self):
        with deepstar_path():
            result = FrameSetModel().delete(1)
            self.assertFalse(result)
