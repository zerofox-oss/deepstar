import os
import json

import cv2
from mtcnn.mtcnn import MTCNN

from deepstar.models.frame_model import FrameModel
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.filesystem.frame_file import FrameFile
from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir
from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.util.debug import debug


class MTCNNFrameSetSelectExtractPlugin:
    """
    This class implements the MTCNNFrameSetSelectExtractPlugin class.
    """

    name = 'face'

    def frame_set_select_extract(self, frame_set_id, opts):
        """
        This method extracts faces from each frame in a frame set.

        :param int frame_set_id: The frame set ID.
        :param dict opts: The dict of opts.
        :rtype: int
        """

        detector = MTCNN()
        offset_percent = 0.2
        min_confidence = 0.9
        debug_ = True if 'debug' in opts else False

        frame_set_path = FrameSetSubDir.path(frame_set_id)

        transform_set_id = TransformSetModel().insert(self.name, frame_set_id)
        transform_set_path = TransformSetSubDir.path(transform_set_id)
        os.makedirs(transform_set_path)

        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        offset = 0

        while True:
            result = FrameModel().list(frame_set_id, length=length,
                                       offset=offset, rejected=False)

            if not result:
                break

            for frame_id, _, rejected in result:
                self._extract_faces(frame_set_path, frame_id,
                                    transform_set_path, transform_set_id,
                                    detector, offset_percent, min_confidence,
                                    debug_)

            offset += length

        return transform_set_id

    def _extract_faces(self, frame_set_path, frame_id, transform_set_path,
                       transform_set_id, detector, offset_percent,
                       min_confidence, debug_):
        """
        This method extracts faces from a frame.

        :param str frame_set_path:The frame set path.
        :param int frame_id: The frame ID.
        :param str transform_set_path: The transform set path.
        :param transform_set_id: The transform set ID.
        :param MTCNN detector: The detector to use to detect faces.
        :param float offset_percent:
        :param float min_confidence: The minimum confidence value required to
            accept/reject a detected face.
        :param bool debug_: True if should place markers on landmarks else
            False if should not.
        :rtype: None
        """

        frame_path = FrameFile.path(frame_set_path, frame_id, 'jpg')
        img = cv2.imread(frame_path)
        img_height, img_width = img.shape[:2]

        results = detector.detect_faces(img)
        for r in results:
            if r['confidence'] < min_confidence:
                continue

            x, y, width, height = r['box']

            adjusted_x = int(max(0, x - (0.5 * width * offset_percent)))
            adjusted_y = int(max(0, y - (0.5 * height * offset_percent)))
            t = x + width + (0.5 * width * offset_percent)
            adjusted_right_x = int(min(img_width, t))
            t = y + height + (0.5 * height * offset_percent)
            adjusted_bottom_y = int(min(img_height, t))

            metadata = {'face': {k: [v[0] - adjusted_x, v[1] - adjusted_y]
                                 for k, v in r['keypoints'].items()}}

            transform_id = TransformModel().insert(transform_set_id, frame_id,
                                                   json.dumps(metadata), 0)

            face_crop = img[adjusted_y:adjusted_bottom_y,
                            adjusted_x:adjusted_right_x]
            output_path = TransformFile.path(transform_set_path, transform_id,
                                             'jpg')

            if debug_ is True:
                for _, v in metadata['face'].items():
                    cv2.drawMarker(face_crop, tuple(v), (0, 0, 255),
                                   markerType=cv2.MARKER_DIAMOND,
                                   markerSize=15, thickness=2)

            cv2.imwrite(output_path, face_crop,
                        [cv2.IMWRITE_JPEG_QUALITY, 100])

            debug(f'Transform with ID {transform_id:08d} at {output_path} '
                  f'extracted from frame with ID {frame_id:08d} at '
                  f'{frame_path}', 4)
