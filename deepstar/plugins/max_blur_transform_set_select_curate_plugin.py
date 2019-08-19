import cv2
import imutils

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.util.debug import debug


class MaxBlurTransformSetSelectCuratePlugin:
    """
    This class implements the MaxBlurTransformSetSelectCuratePlugin class.
    """

    name = 'max_blur'

    def transform_set_select_curate(self, transform_set_id, opts):
        """
        This method automatically curates a transform set and rejects
        transforms that are more blurry than the 'max-blur'.

        :param int transform_set_id: The transform set ID.
        :param dict opts: The dict of options.
        :raises: ValueError
        :rtype: None
        """

        if 'max-blur' not in opts:
            raise ValueError(
                'The max-blur option is required but was not supplied')

        max_blur = float(opts['max-blur'])

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

                image = cv2.imread(p2)

                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                h, w = image.shape[:2]

                # recommendation to scale down image to ~500
                if h > 600 or w > 600:
                    # imutils.resize preserves aspect ratio.
                    image = imutils.resize(image, width=500, height=500)

                score = cv2.Laplacian(image, cv2.CV_64F).var()

                if score < max_blur:
                    transform_model.update(transform[0], rejected=1)

                    debug(f'Transform with ID {transform[0]:08d} rejected',
                          4)

            offset += length
