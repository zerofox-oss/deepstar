import sqlite3
import unittest

from deepstar.models.frame_model import FrameModel
from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel

from .. import deepstar_path


class TestTransformModel(unittest.TestCase):
    """
    This class tests the TransformModel class.
    """

    def test_select(self):
        with deepstar_path():
            FrameSetModel().insert(None)
            FrameModel().insert(1, 0)

            TransformSetModel().insert('test', 1)

            transform_model = TransformModel()
            transform_model.insert(1, 1, '{}', 0)

            result = transform_model.select(1)
            self.assertEqual(result, (1, 1, 1, '{}', 0))

    def test_select_fails_to_select_transform(self):
        with deepstar_path():
            result = TransformModel().select(1)
            self.assertIsNone(result)

    def test_insert(self):
        with deepstar_path():
            FrameSetModel().insert(None)
            FrameModel().insert(1, 0)

            TransformSetModel().insert('test', 1)

            transform_model = TransformModel()
            transform_id = transform_model.insert(1, 1, '{}', 0)
            self.assertEqual(transform_id, 1)

            result = transform_model.select(1)
            self.assertEqual(result, (1, 1, 1, '{}', 0))

    def test_fk_transform_sets_fk_transforms_sets_constraint(self):
        with deepstar_path():
            with self.assertRaises(sqlite3.IntegrityError):
                TransformModel().insert(1, 1, '{}', 0)

    def test_fk_transform_sets_fk_frames_constraint(self):
        with deepstar_path():
            FrameSetModel().insert(None)

            TransformSetModel().insert('test', 1)

            with self.assertRaises(sqlite3.IntegrityError):
                TransformModel().insert(1, 1, '{}', 0)

    def test_fk_transform_sets_on_delete_cascade(self):
        with deepstar_path():
            FrameSetModel().insert(None)
            FrameModel().insert(1, 0)

            transform_set_model = TransformSetModel()
            transform_set_model.insert('test', 1)
            transform_model = TransformModel()
            transform_model.insert(1, 1, '{}', 0)
            self.assertEqual(transform_model.list(1), [(1, 1, 1, '{}', 0)])
            transform_set_model.delete(1)
            self.assertIsNone(transform_model.list(1))

    def test_list(self):
        with deepstar_path():
            FrameSetModel().insert(None)
            FrameModel().insert(1, 0)

            TransformSetModel().insert('test', 1)

            transform_model = TransformModel()
            transform_model.insert(1, 1, '{}', 0)
            transform_model.insert(1, 1, '{}', 1)
            transform_model.insert(1, 1, '{}', 0)

            result = transform_model.list(1)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0], (1, 1, 1, '{}', 0))
            self.assertEqual(result[1], (2, 1, 1, '{}', 1))
            self.assertEqual(result[2], (3, 1, 1, '{}', 0))

            result = transform_model.list(1, length=2)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], (1, 1, 1, '{}', 0))
            self.assertEqual(result[1], (2, 1, 1, '{}', 1))

            result = transform_model.list(1, offset=1)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], (2, 1, 1, '{}', 1))
            self.assertEqual(result[1], (3, 1, 1, '{}', 0))

            result = transform_model.list(1, length=1, offset=1)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], (2, 1, 1, '{}', 1))

            result = transform_model.list(1, rejected=False)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], (1, 1, 1, '{}', 0))
            self.assertEqual(result[1], (3, 1, 1, '{}', 0))

    def test_list_fails_to_list_transform_set(self):
        with deepstar_path():
            result = TransformModel().list(1)
            self.assertIsNone(result)

    def test_update(self):
        with deepstar_path():
            FrameSetModel().insert(None)
            FrameModel().insert(1, 0)

            TransformSetModel().insert('test', 1)

            transform_model = TransformModel()
            transform_model.insert(1, 1, 'test1', 0)

            result = transform_model.select(1)
            self.assertEqual(result, (1, 1, 1, 'test1', 0))

            result = transform_model.update(1, 'test2', 1)
            self.assertTrue(result)

            result = transform_model.select(1)
            self.assertEqual(result, (1, 1, 1, 'test2', 1))

    def test_update_fails_to_update_transform(self):
        with deepstar_path():
            result = TransformModel().update(1, '{}', 1)
            self.assertFalse(result)

    def test_count(self):
        with deepstar_path():
            FrameSetModel().insert(None)

            frame_model = FrameModel()
            frame_model.insert(1, 0)
            frame_model.insert(1, 0)
            frame_model.insert(1, 0)

            TransformSetModel().insert('test', 1)

            transform_model = TransformModel()
            transform_model.insert(1, 1, '{}', 0)
            transform_model.insert(1, 2, '{}', 0)
            transform_model.insert(1, 3, '{}', 0)

            self.assertEqual(frame_model.count(1), 3)

    def test_count_rejected_false(self):
        with deepstar_path():
            FrameSetModel().insert(None)

            frame_model = FrameModel()
            frame_model.insert(1, 0)
            frame_model.insert(1, 0)
            frame_model.insert(1, 0)

            TransformSetModel().insert('test', 1)

            transform_model = TransformModel()
            transform_model.insert(1, 1, '{}', 0)
            transform_model.insert(1, 2, '{}', 1)
            transform_model.insert(1, 3, '{}', 0)

            self.assertEqual(transform_model.count(1, rejected=False), 2)

    def test_count_fails_to_count(self):
        with deepstar_path():
            self.assertEqual(TransformModel().count(1), 0)
