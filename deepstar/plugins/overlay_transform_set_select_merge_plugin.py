import os

import cv2

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.util.debug import debug


class OverlayTransformSetSelectMergePlugin:
    """
    This class implements the OverlayTransformSetSelectMergePlugin class.
    """

    name = 'overlay'

    def transform_set_select_merge(self, transform_set_ids, opts):
        """
        This method merges transform sets overlaying transform set 1 onto
        transform set 2 at a specified position.

        :param list(int) transform_set_ids: The transform set IDs.
        :param dict opts: The dict of options.
        :raises: ValueError
        :rtype: int
        """

        if len(transform_set_ids) != 2:
            raise ValueError('Exactly two transform set IDs must be supplied')

        x1 = int(opts['x1']) if ('x1' in opts) else None
        y1 = int(opts['y1']) if ('y1' in opts) else None

        if x1 is None or y1 is None:
            raise ValueError(
                'The x1 and y1 options are required but were not supplied')

        transform_set_id_1 = transform_set_ids[0]
        transform_set_id_2 = transform_set_ids[1]

        transform_model = TransformModel()

        transform_set_1_count = transform_model.count(transform_set_id_1,
                                                      rejected=False)
        transform_set_2_count = transform_model.count(transform_set_id_2,
                                                      rejected=False)

        if transform_set_1_count != transform_set_2_count:
            raise ValueError(
                'Both transform sets must have the same number of '
                'non-rejected transforms (be the same length)')

        transform_set_id = TransformSetModel().insert('overlay', None, None)

        p1 = TransformSetSubDir.path(transform_set_id)

        os.makedirs(p1)

        p2 = TransformSetSubDir.path(transform_set_id_1)
        p3 = TransformSetSubDir.path(transform_set_id_2)
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        offset = 0

        while True:
            transforms_1 = transform_model.list(transform_set_id_1,
                                                length=length, offset=offset,
                                                rejected=False)
            transforms_2 = transform_model.list(transform_set_id_2,
                                                length=length, offset=offset,
                                                rejected=False)

            if not transforms_1:
                break

            for i in range(0, len(transforms_1)):
                transform_id_1 = transforms_1[i][0]
                transform_id_2 = transforms_2[i][0]

                image_path_1 = TransformFile.path(p2, transform_id_1, 'jpg')
                image_path_2 = TransformFile.path(p3, transform_id_2, 'jpg')

                transform_id = transform_model.insert(transform_set_id, None,
                                                      None, 0)

                image_path_3 = TransformFile.path(p1, transform_id, 'jpg')

                image_1 = cv2.imread(image_path_1)

                height_1, width_1 = image_1.shape[:2]

                image_2 = cv2.imread(image_path_2)

                image_2[y1:y1 + height_1, x1:x1 + width_1] = image_1

                cv2.imwrite(image_path_3, image_2,
                            [cv2.IMWRITE_JPEG_QUALITY, 100])

                debug(f'Transforms with ID {transform_id_1:08d} at '
                      f'{image_path_1} and {transform_id_2:08d} at '
                      f'{image_path_2} merged as ID {transform_id:08d} at '
                      f'{image_path_3}', 4)

            offset += length

        return transform_set_id
