import os

import cv2

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.util.debug import debug
from deepstar.util.cv import overlay_transparent_image


class OverlayImageTransformSetSelectMergePlugin:
    """
    This class implements the OverlayImageTransformSetSelectMergePlugin class.
    """

    name = 'overlay_image'

    def transform_set_select_merge(self, transform_set_ids, opts):
        """
        This method merges one transform set with one image. This is to say
        that one image is overlaid onto every transform in a transform set and
        at a specified position.

        :param list(int) transform_set_ids: The transform set IDs.
        :param dict opts: The dict of options.
        :raises: ValueError
        :rtype: int
        """

        if len(transform_set_ids) != 1:
            raise ValueError('Exactly one transform set ID must be supplied')

        image_path_1 = opts.get('image-path', None)
        x1 = int(opts['x1']) if ('x1' in opts) else None
        y1 = int(opts['y1']) if ('y1' in opts) else None

        if image_path_1 is None or x1 is None or y1 is None:
            raise ValueError(
                'The image-path, x1 and y1 options are required but were not '
                'supplied')

        if not os.path.isfile(image_path_1):
            raise ValueError(
                f'The image path {image_path_1} does not exist or is not a '
                f'file')

        transform_set_id = transform_set_ids[0]

        transform_model = TransformModel()

        transform_set_id_ = TransformSetModel().insert('overlay_image', None,
                                                       None)

        p1 = TransformSetSubDir.path(transform_set_id_)

        os.makedirs(p1)

        p2 = TransformSetSubDir.path(transform_set_id)
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        offset = 0

        image_1 = cv2.imread(image_path_1, cv2.IMREAD_UNCHANGED)

        while True:
            transforms = transform_model.list(transform_set_id,
                                              length=length, offset=offset,
                                              rejected=False)

            if not transforms:
                break

            for transform in transforms:
                transform_id = transform_model.insert(transform_set_id_, None,
                                                      None, 0)

                image_path_2 = TransformFile.path(p2, transform[0], 'jpg')

                image_2 = cv2.imread(image_path_2)

                image_3 = overlay_transparent_image(image_2, image_1, x1, y1)

                image_path_3 = TransformFile.path(p1, transform_id, 'jpg')

                cv2.imwrite(image_path_3, image_3,
                            [cv2.IMWRITE_JPEG_QUALITY, 100])

                debug(f'{image_path_1} and transform with ID '
                      f'{transform[0]:08d} at {image_path_2} merged as ID '
                      f'{transform_id:08d} at {image_path_3}', 4)

            offset += length

        return transform_set_id_
