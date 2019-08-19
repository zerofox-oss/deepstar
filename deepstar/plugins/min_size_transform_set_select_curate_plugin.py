import cv2

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.util.debug import debug


class MinSizeTransformSetSelectCuratePlugin:
    """
    This class implements the MinSizeTransformSetSelectCuratePlugin class.
    """

    name = 'min_size'

    def transform_set_select_curate(self, transform_set_id, opts):
        """
        This method automatically curates a transform set and rejects
        transforms with width or height less than 'min-size'.

        :param int transform_set_id: The transform set ID.
        :param dict opts: The dict of options.
        :raises: ValueError
        :rtype: None
        """

        if 'min-size' not in opts:
            raise ValueError(
                'The min-size option is required but was not supplied')

        min_length = int(opts['min-size'])

        transform_model = TransformModel()
        length = 100
        offset = 0
        p1 = TransformSetSubDir.path(transform_set_id)

        while True:
            transforms = transform_model.list(transform_set_id, length=length,
                                              offset=offset)
            if not transforms:
                break

            for transform in transforms:
                p2 = TransformFile.path(p1, transform[0], 'jpg')

                debug(f'Curating transform with ID {transform[0]:08d} at {p2}',
                      4)

                h, w = cv2.imread(p2).shape[:2]

                if h < min_length or w < min_length:
                    transform_model.update(transform[0], rejected=1)

                    debug(f'Transform with ID {transform[0]:08d} rejected',
                          4)

            offset += length
