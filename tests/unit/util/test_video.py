import os
import unittest

import cv2

from deepstar.util.tempdir import tempdir
from deepstar.util.video import create_one_video_file_from_one_image_file, \
    create_one_video_file_from_many_image_files


class TestVideo(unittest.TestCase):
    """
    This class tests the video module.
    """

    def test_create_one_video_file_from_one_image_file(self):
        image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0001.jpg'  # noqa

        with tempdir() as tempdir_:
            video_path = os.path.join(tempdir_, 'video.mp4')

            ret = create_one_video_file_from_one_image_file(image_0001,
                                                            video_path)

            self.assertTrue(ret)

            vc = cv2.VideoCapture(video_path)

            try:
                self.assertTrue(vc.isOpened())
                self.assertEqual(vc.get(cv2.CAP_PROP_FRAME_COUNT), 1)
            finally:
                vc.release()

    def test_create_one_video_file_from_one_image_file_frame_count(self):
        image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0001.jpg'  # noqa

        with tempdir() as tempdir_:
            video_path = os.path.join(tempdir_, 'video.mp4')

            ret = create_one_video_file_from_one_image_file(image_0001,
                                                            video_path,
                                                            frame_count=5)

            self.assertTrue(ret)

            vc = cv2.VideoCapture(video_path)

            try:
                self.assertTrue(vc.isOpened())
                self.assertEqual(vc.get(cv2.CAP_PROP_FRAME_COUNT), 5)
            finally:
                vc.release()

    def test_create_one_video_file_from_one_image_file_fails_to_open_image(self):  # noqa
        image_0001 = 'test'

        with tempdir() as tempdir_:
            video_path = os.path.join(tempdir_, 'video.mp4')

            ret = create_one_video_file_from_one_image_file(image_0001,
                                                            video_path,
                                                            frame_count=5)
            self.assertFalse(ret)

    def test_create_one_video_file_from_many_image_files(self):
        image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0001.jpg'  # noqa

        with tempdir() as tempdir_:
            video_path = os.path.join(tempdir_, 'video.mp4')

            def image_paths():
                for _ in range(0, 5):
                    yield image_0001

            ret = create_one_video_file_from_many_image_files(image_paths, video_path)  # noqa

            self.assertTrue(ret)

            vc = cv2.VideoCapture(video_path)

            try:
                self.assertTrue(vc.isOpened())
                self.assertEqual(vc.get(cv2.CAP_PROP_FRAME_COUNT), 5)
            finally:
                vc.release()
