import os
import shutil

from deepstar.filesystem.frame_file import FrameFile
from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir
from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.frame_model import FrameModel
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.util.debug import debug


class TransformSetFrameSetSelectExtractPlugin:
    """
    This class implements the TransformSetFrameSetSelectExtractPlugin class.
    """

    name = 'transform_set'

    def frame_set_select_extract(self, frame_set_id, opts):
        """
        This method extracts a frame set to a transform set.

        :param int frame_set_id: The frame set ID.
        :param dict opts: The dict of options.
        :rtype: int
        """

        transform_set_id = TransformSetModel().insert('transform_set',
                                                      frame_set_id)

        p1 = TransformSetSubDir.path(transform_set_id)

        os.mkdir(p1)

        frame_model = FrameModel()
        transform_model = TransformModel()
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        offset = 0
        p2 = FrameSetSubDir.path(frame_set_id)

        while True:
            frames = frame_model.list(frame_set_id, length=length,
                                      offset=offset, rejected=False)

            if not frames:
                break

            for frame in frames:
                transform_id = transform_model.insert(transform_set_id,
                                                      frame[0], None, 0)

                p3 = FrameFile.path(p2, frame[0], 'jpg')
                p4 = TransformFile.path(p1, transform_id, 'jpg')

                shutil.copy(p3, p4)

                debug(f'Transform with ID {transform_id:08d} at {p4} '
                      f'extracted from frame with ID {frame[0]:08d} at '
                      f'{p3}', 4)

            offset += length

        return transform_set_id
