import unittest

from deepstar.models.video_model import VideoModel

from .. import deepstar_path


class TestVideoModel(unittest.TestCase):
    """
    This class tests the VideoModel class.
    """

    def test_select(self):
        with deepstar_path():
            video_model = VideoModel()
            video_id = video_model.insert('test1', 'test2')
            self.assertEqual(video_id, 1)
            result = video_model.select(1)
            self.assertEqual(result, (1, 'test1', 'test2', None))

    def test_select_fails_to_select_video(self):
        with deepstar_path():
            result = VideoModel().select(1)
            self.assertIsNone(result)

    def test_insert(self):
        with deepstar_path():
            video_model = VideoModel()
            video_id = video_model.insert('test1', 'test2')
            self.assertEqual(video_id, 1)
            result = video_model.select(1)
            self.assertEqual(result, (1, 'test1', 'test2', None))

    def test_update(self):
        with deepstar_path():
            video_model = VideoModel()

            video_model.insert('test1', 'test2')

            result = video_model.select(1)
            self.assertEqual(result, (1, 'test1', 'test2', None))

            video_model.update(1, uri='test3')

            result = video_model.select(1)
            self.assertEqual(result, (1, 'test3', 'test2', None))

    def test_update_fails_to_update_transform(self):
        with deepstar_path():
            result = VideoModel().update(1)
            self.assertFalse(result)

    def test_list(self):
        with deepstar_path():
            video_model = VideoModel()
            video_model.insert('test1', 'test2')
            video_model.insert('test3', 'test4')
            video_model.insert('test5', 'test6')
            result = video_model.list()
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0], (1, 'test1', 'test2', None))
            self.assertEqual(result[1], (2, 'test3', 'test4', None))
            self.assertEqual(result[2], (3, 'test5', 'test6', None))

    def test_delete(self):
        with deepstar_path():
            video_model = VideoModel()
            video_model.insert('test1', 'test2')
            result = video_model.select(1)
            self.assertEqual(result, (1, 'test1', 'test2', None))
            result = video_model.delete(1)
            self.assertTrue(result)
            result = video_model.select(1)
            self.assertIsNone(result)

    def test_delete_fails_to_delete_video(self):
        with deepstar_path():
            result = VideoModel().delete(1)
            self.assertFalse(result)
