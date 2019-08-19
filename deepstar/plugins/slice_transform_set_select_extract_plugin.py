import os
import shutil

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.util.debug import debug


class SliceTransformSetSelectExtractPlugin:
    """
    This class implements the SliceTransformSetSelectExtractPlugin class.
    """

    name = 'slice'

    def transform_set_select_extract(self, transform_set_id, opts):
        """
        This method extracts a slice from a transform set (a subset).

        :param int transform_set_id: The transform set ID.
        :param dict opts: The dict of opts.
        :raises: ValueError
        :rtype: int
        """

        start = int(opts['start']) if ('start' in opts) else None
        end = int(opts['end']) if ('end' in opts) else None

        if start is None or end is None:
            raise ValueError(
                'The start and end options are required but were not '
                'supplied')

        transform_set_model = TransformSetModel()

        result = transform_set_model.select(transform_set_id)

        transform_set_id_ = TransformSetModel().insert('slice', result[2],
                                                       transform_set_id)

        p1 = TransformSetSubDir.path(transform_set_id_)

        os.makedirs(p1)

        p2 = TransformSetSubDir.path(transform_set_id)
        transform_model = TransformModel()
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        offset = 0
        flag = True

        while flag:
            transforms = transform_model.list(transform_set_id, length=length,
                                              offset=offset, rejected=False)

            if not transforms:
                break

            for transform in transforms:
                if transform[0] < start:
                    continue

                if transform[0] > end:
                    flag = False
                    break

                transform_id = transform_model.insert(transform_set_id_,
                                                      transform[2],
                                                      transform[3],
                                                      transform[4])

                p3 = TransformFile.path(p2, transform[0], 'jpg')
                p4 = TransformFile.path(p1, transform_id, 'jpg')

                shutil.copy(p3, p4)

                debug(f'Transform with ID {transform_id:08d} at {p4} '
                      f'extracted from transform with ID {transform[0]:08d} '
                      f'at {p3}', 4)

            offset += length

        return transform_set_id_
