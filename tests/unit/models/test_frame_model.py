import sqlite3
import unittest

from deepstar.models.frame_model import FrameModel
from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.video_model import VideoModel

from .. import deepstar_path


class TestFrameModel(unittest.TestCase):
    """
    This class tests the FrameModel class.
    """

    def test_select(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            FrameSetModel().insert(1)

            frame_model = FrameModel()
            frame_model.insert(1, 0)

            result = frame_model.select(1)
            self.assertEqual(result, (1, 1, 0))

    def test_select_fails_to_select_frame(self):
        with deepstar_path():
            result = FrameModel().select(1)
            self.assertIsNone(result)

    def test_insert(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            FrameSetModel().insert(1)

            frame_model = FrameModel()
            frame_id = frame_model.insert(1, 0)
            self.assertEqual(frame_id, 1)

            result = frame_model.select(1)
            self.assertEqual(result, (1, 1, 0))

    def test_fk_frame_sets_constraint(self):
        with deepstar_path():
            with self.assertRaises(sqlite3.IntegrityError):
                FrameModel().insert(1, 0)

    def test_fk_frame_sets_on_delete_cascade(self):
        with deepstar_path():
            frame_set_model = FrameSetModel()
            frame_set_model.insert(1)
            frame_model = FrameModel()
            frame_model.insert(1, 0)
            self.assertEqual(frame_model.list(1), [(1, 1, 0)])
            frame_set_model.delete(1)
            self.assertIsNone(frame_model.list(1))

    def test_list(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            FrameSetModel().insert(1)

            frame_model = FrameModel()
            frame_model.insert(1, 0)
            frame_model.insert(1, 1)
            frame_model.insert(1, 0)

            result = frame_model.list(1)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0], (1, 1, 0))
            self.assertEqual(result[1], (2, 1, 1))
            self.assertEqual(result[2], (3, 1, 0))

            result = frame_model.list(1, length=2)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], (1, 1, 0))
            self.assertEqual(result[1], (2, 1, 1))

            result = frame_model.list(1, offset=1)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], (2, 1, 1))
            self.assertEqual(result[1], (3, 1, 0))

            result = frame_model.list(1, length=1, offset=1)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], (2, 1, 1))

            result = frame_model.list(1, rejected=False)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], (1, 1, 0))
            self.assertEqual(result[1], (3, 1, 0))

    def test_list_fails_to_list_frame_set(self):
        with deepstar_path():
            result = FrameModel().list(1)
            self.assertIsNone(result)

    def test_update(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            FrameSetModel().insert(1)

            frame_model = FrameModel()
            frame_model.insert(1, 0)

            result = frame_model.select(1)
            self.assertEqual(result, (1, 1, 0))

            result = frame_model.update(1, 1)
            self.assertTrue(result)

            result = frame_model.select(1)
            self.assertEqual(result, (1, 1, 1))

    def test_update_fails_to_update_frame(self):
        with deepstar_path():
            result = FrameModel().update(1, 1)
            self.assertFalse(result)

    def test_count(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            FrameSetModel().insert(1)

            frame_model = FrameModel()
            frame_model.insert(1, 0)
            frame_model.insert(1, 0)
            frame_model.insert(1, 0)

            self.assertEqual(frame_model.count(1), 3)

    def test_count_rejected_false(self):
        with deepstar_path():
            VideoModel().insert('test1', 'test2')

            FrameSetModel().insert(1)

            frame_model = FrameModel()
            frame_model.insert(1, 0)
            frame_model.insert(1, 1)
            frame_model.insert(1, 0)

            self.assertEqual(frame_model.count(1, rejected=False), 2)

    def test_count_fails_to_count(self):
        with deepstar_path():
            self.assertEqual(FrameModel().count(1), 0)
