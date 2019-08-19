import json
import mock
import os
import shutil
import unittest

import cv2
import numpy as np

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.filesystem.video_file import VideoFile
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.models.video_model import VideoModel
from deepstar.plugins.default_video_select_extract_plugin import \
    DefaultVideoSelectExtractPlugin
from deepstar.plugins.pad_transform_set_select_extract_plugin import \
    PadTransformSetSelectExtractPlugin


from deepstar.plugins.mouth_transform_set_select_extract_plugin import \
    MouthTransformSetSelectExtractPlugin
from deepstar.plugins.mtcnn_frame_set_select_extract_plugin import \
    MTCNNFrameSetSelectExtractPlugin

from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.frame_model import FrameModel
from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir
from deepstar.filesystem.frame_file import FrameFile

from .. import deepstar_path


class TestMouthTransformSetSelectExtractPlugin(unittest.TestCase):
    """
    This class implements tests for the MouthTransformSetSelectExtractPlugin
    class.
    """

    def mock_transform_set(self):
        image_0006 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0006.jpg'  # noqa

        FrameSetModel().insert('1')

        FrameModel().insert(1, 0)

        p1 = FrameSetSubDir.path(1)
        os.mkdir(p1)

        shutil.copy(image_0006, FrameFile.path(p1, 1, 'jpg'))

        MTCNNFrameSetSelectExtractPlugin().frame_set_select_extract(1, {})
    
    def test_transform_set_select_extract_mouth(self):
        with deepstar_path():
            self.mock_transform_set()

            tid = MouthTransformSetSelectExtractPlugin().transform_set_select_extract(1, {})  # noqa

            self.assertEqual(tid, 2)

            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'mouth', 1, 1))
