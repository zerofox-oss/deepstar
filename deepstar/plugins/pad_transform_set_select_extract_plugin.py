import os
import json

import cv2
import numpy as np

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.util.debug import debug


class PadTransformSetSelectExtractPlugin:
    """
    This class implements the PadTransformSetSelectExtractPlugin class.
    """

    name = 'pad'

    def transform_set_select_extract(self, transform_set_id, opts):
        """
        This method pads each transform in a transform set.

        :param int transform_set_id: The transform set ID.
        :param dict opts: The dict of options.
        :rtype: int
        """

        size = int(opts.get('size', 299))

        transform_set_path = TransformSetSubDir.path(transform_set_id)
        _, _, frame_set_id, _ = TransformSetModel().select(transform_set_id)

        target_set_id = TransformSetModel().insert(
            f'{self.name}', frame_set_id, transform_set_id)

        target_path = TransformSetSubDir.path(target_set_id)
        os.makedirs(target_path)

        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        offset = 0

        while True:
            result = TransformModel().list(transform_set_id, length=length,
                                           offset=offset, rejected=False)

            if not result:
                break

            for transform_id, _, frame_id, metadata, rejected in result:
                self._pad(transform_set_path, transform_id, frame_id, metadata,
                          target_set_id, size)

            offset += length

        return target_set_id

    def _pad(self, transform_set_path, transform_id, frame_id, metadata,
             target_set_id, size):
        """
        This method pads a transform.

        :param str transform_set_path: The transform set path.
        :param int transform_id: The transform ID.
        :param int frame_id: The frame ID.
        :param str metadata: Metadata for the transform.
        :param int target_set_id: The new transform set ID.
        :param int size: The size to which to pad.
        :rtype: None
        """

        transform_path = TransformFile().path(transform_set_path, transform_id,
                                              'jpg')
        img = cv2.imread(transform_path)
        img_height, img_width = img.shape[:2]

        img_padded = np.zeros((size, size, 3), dtype=np.uint8)
        img_padded[:img_height, :img_width, :] = img.copy()

        target_id = TransformModel().insert(target_set_id, frame_id,
                                            json.dumps(metadata), 0)
        output_path = TransformFile.path(
            TransformSetSubDir.path(target_set_id), target_id, 'jpg')

        cv2.imwrite(output_path, img_padded, [cv2.IMWRITE_JPEG_QUALITY, 100])

        debug(f'Transform with ID {target_id:08d} at {output_path} extracted '
              f'from transform with ID {transform_id:08d} at {transform_path}',
              4)
