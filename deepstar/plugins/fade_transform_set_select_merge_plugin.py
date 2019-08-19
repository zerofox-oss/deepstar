import os
import shutil

import cv2

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.util.debug import debug


class FadeTransformSetSelectMergePlugin:
    """
    This class implements the FadeTransformSetSelectMergePlugin class.
    """

    name = 'fade'

    def transform_set_select_merge(self, transform_set_ids, opts):
        """
        This method merges transform sets w/ a fade effect applied.

        :param list(int) transform_set_ids: The transform set IDs.
        :param dict opts: The dict of options.
        :raises: ValueError
        :rtype: int
        """

        if len(transform_set_ids) != 2:
            raise ValueError('Exactly two transform set IDs must be supplied')

        if 'frame-count' not in opts:
            raise ValueError(
                'The frame-count option is required but was not supplied')

        frame_count = int(opts['frame-count'])

        if frame_count < 1:
            raise ValueError('Frame count must be 1 or greater')

        transform_set_id_1 = transform_set_ids[0]
        transform_set_id_2 = transform_set_ids[1]

        transform_model = TransformModel()

        transform_set_1_count = transform_model.count(transform_set_id_1,
                                                      rejected=False)
        transform_set_2_count = transform_model.count(transform_set_id_2,
                                                      rejected=False)

        if transform_set_1_count <= frame_count or \
           transform_set_2_count <= frame_count:
            raise ValueError(
                'Both transform sets must be greater than frame count')

        transform_set_id = TransformSetModel().insert('fade', None, None)

        p1 = TransformSetSubDir.path(transform_set_id)

        os.makedirs(p1)

        p2 = TransformSetSubDir.path(transform_set_id_1)
        p3 = TransformSetSubDir.path(transform_set_id_2)
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        offset = 0
        flag = True

        while flag:
            transforms = transform_model.list(transform_set_id_1,
                                              length=length, offset=offset,
                                              rejected=False)

            for transform in transforms:
                transform_id = transform_model.insert(transform_set_id,
                                                      transform[2],
                                                      transform[3],
                                                      transform[4])

                p4 = TransformFile.path(p2, transform[0], 'jpg')
                p5 = TransformFile.path(p1, transform_id, 'jpg')

                shutil.copy(p4, p5)

                debug(f'Transform with ID {transform[0]:08d} at {p4} '
                      f'merged as ID {transform_id:08d} at {p5}', 4)

                offset += 1

                if transform_set_1_count - offset == frame_count:
                    flag = False
                    break

        transforms_1 = transform_model.list(transform_set_id_1,
                                            length=frame_count, offset=offset,
                                            rejected=False)
        transforms_2 = transform_model.list(transform_set_id_2,
                                            length=frame_count, offset=0,
                                            rejected=False)

        for i in range(0, frame_count):
            transform_id_1 = transforms_1[i][0]
            transform_id_2 = transforms_2[i][0]

            image_path_1 = TransformFile.path(p2, transform_id_1, 'jpg')
            image_path_2 = TransformFile.path(p3, transform_id_2, 'jpg')

            transform_id = transform_model.insert(transform_set_id, None, None,
                                                  0)

            image_path_3 = TransformFile.path(p1, transform_id, 'jpg')

            image_1 = cv2.imread(image_path_1)
            image_2 = cv2.imread(image_path_2)
            alpha = 1.0 - float(i + 1) / float(frame_count)
            image_3 = cv2.addWeighted(image_1, alpha, image_2, 1.0 - alpha, 0)

            cv2.imwrite(image_path_3, image_3, [cv2.IMWRITE_JPEG_QUALITY, 100])

            debug(f'Transforms with ID {transform_id_1:08d} at {image_path_1} '
                  f'and {transform_id_2:08d} at {image_path_2} merged with '
                  f'alpha {alpha} as ID {transform_id:08d} at {image_path_3}',
                  4)

        offset = frame_count

        while True:
            transforms = transform_model.list(transform_set_id_2,
                                              length=length, offset=offset,
                                              rejected=False)

            if not transforms:
                break

            for transform in transforms:
                transform_id = transform_model.insert(transform_set_id,
                                                      transform[2],
                                                      transform[3],
                                                      transform[4])

                p4 = TransformFile.path(p3, transform[0], 'jpg')
                p5 = TransformFile.path(p1, transform_id, 'jpg')

                shutil.copy(p4, p5)

                debug(f'Transform with ID {transform[0]:08d} at {p4} '
                      f'merged as ID {transform_id:08d} at {p5}', 4)

                offset += 1

        return transform_set_id
