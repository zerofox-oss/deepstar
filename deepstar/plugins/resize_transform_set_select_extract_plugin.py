import os

import cv2
import imutils

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.util.debug import debug


class ResizeTransformSetSelectExtractPlugin:
    """
    This class implements the ResizeTransformSetSelectExtractPlugin class.
    """

    name = 'resize'

    def transform_set_select_extract(self, transform_set_id, opts):
        """
        This method resizes each transform in a transform set.

        :param int transform_set_id: The transform set ID.
        :param dict opts: The dict of options.
        :raises: ValueError
        :rtype: None
        """

        height = int(opts['height']) if ('height' in opts) else None
        width = int(opts['width']) if ('width' in opts) else None

        if height is None and width is None:
            raise ValueError(
                'The height or width options are required but were not '
                'supplied')

        transform_set_model = TransformSetModel()

        result = transform_set_model.select(transform_set_id)

        transform_set_id_ = TransformSetModel().insert('resize', result[2],
                                                       transform_set_id)

        p1 = TransformSetSubDir.path(transform_set_id_)

        os.makedirs(p1)

        p2 = TransformSetSubDir.path(transform_set_id)
        transform_model = TransformModel()
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        offset = 0

        while True:
            transforms = transform_model.list(transform_set_id, length=length,
                                              offset=offset, rejected=False)

            if not transforms:
                break

            for transform in transforms:
                transform_id = transform_model.insert(transform_set_id_,
                                                      transform[2],
                                                      transform[3],
                                                      transform[4])

                p3 = TransformFile.path(p2, transform[0], 'jpg')
                p4 = TransformFile.path(p1, transform_id, 'jpg')

                image_1 = cv2.imread(p3)

                if width is not None:
                    image_2 = imutils.resize(image_1, width=width)
                else:
                    image_2 = imutils.resize(image_1, height=height)

                cv2.imwrite(p4, image_2, [cv2.IMWRITE_JPEG_QUALITY, 100])

                debug(f'Transform with ID {transform_id:08d} at {p4} '
                      f'extracted from transform with ID {transform[0]:08d} '
                      f'at {p3}', 4)

            offset += length

        return transform_set_id_
