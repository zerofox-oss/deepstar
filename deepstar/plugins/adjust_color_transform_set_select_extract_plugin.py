import os
import re

import cv2
import numpy as np

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.util.cv import adjust_color
from deepstar.util.debug import debug


class AdjustColorTransformSetSelectExtractPlugin:
    """
    This class implements the AdjustTransformSetSelectExtractPlugin class.
    """

    name = 'adjust_color'

    def transform_set_select_extract(self, transform_set_id, opts):
        """
        This method adjusts color for each transform in a transform set.

        :param int transform_set_id: The transform set ID.
        :param dict opts: The dict of options.
        :raises: ValueError
        :rtype: None
        """

        r = opts.get('r', None)
        g = opts.get('g', None)
        b = opts.get('b', None)

        if r is None and g is None and b is None:
            raise ValueError(
                'The r, g and/or b options are required but were not supplied')

        for channel in [r, g, b]:
            if channel is not None:
                if not re.match('^[+,\\-]\\d+$', channel):
                    raise ValueError(
                        'A color adjustment option value must be formatted as '
                        '+/- followed by a number (e.g. --r=+10)')

        color_adjustments = []

        for index, channel in enumerate([b, g, r]):
            if channel is not None:
                color_adjustments.append(
                    [index, int(channel[1:]),
                     True if (channel[:1] == '+') else False])
            else:
                color_adjustments.append(None)

        transform_set_model = TransformSetModel()

        result = transform_set_model.select(transform_set_id)

        transform_set_id_ = TransformSetModel().insert('adjust_color',
                                                       result[2],
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

                image = cv2.imread(p3)

                image = image.astype(np.short)

                for color_adjustment in color_adjustments:
                    if color_adjustment is not None:
                        image = adjust_color(image, color_adjustment[0],
                                             color_adjustment[1],
                                             color_adjustment[2])

                cv2.imwrite(p4, image, [cv2.IMWRITE_JPEG_QUALITY, 100])

                debug(f'Transform with ID {transform_id:08d} at {p4} '
                      f'extracted from transform with ID {transform[0]:08d} '
                      f'at {p3}', 4)

            offset += length

        return transform_set_id_
