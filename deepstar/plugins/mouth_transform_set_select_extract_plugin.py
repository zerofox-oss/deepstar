import os
import json

import cv2

from deepstar.models.transform_model import TransformModel
from deepstar.filesystem.transform_file import TransformFile
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir


class MouthTransformSetSelectExtractPlugin:
    """
    This class implements the MouthTransformSetSelectExtractPlugin class.
    """

    name = 'mouth'

    def transform_set_select_extract(self, transform_set_id, opts):
        """
        This method extracts just the mouth from an image of a face.

        :param int transform_set_id: The transform set ID.
        :rtype: int
        """

        self._offset_percent = int(opts.get('offset-percent', 20)) / 100

        transform_set_path = TransformSetSubDir.path(transform_set_id)
        _, _, frame_set_id, _ = TransformSetModel().select(transform_set_id)

        target_set_id = TransformSetModel().insert(
            f'{self.name}', frame_set_id, transform_set_id)

        target_path = TransformSetSubDir.path(target_set_id)
        os.makedirs(target_path)

        result = TransformModel().list(transform_set_id)

        for transform_id, _, frame_id, metadata, rejected in result:
            if rejected == 1:
                continue

            metadata = json.loads(metadata)
            self._get_mouth(transform_set_path, transform_id, frame_id,
                            metadata, target_set_id)

        return target_set_id

    def _get_mouth(self, transform_set_path, transform_id, frame_id, metadata,
                   target_set_id):
        """
        This method extracts a square cropping of a mouth.

        :param str transform_set_path: The transform set path.
        :param int transform_id: The transform ID.
        :param int frame_id: The frame ID.
        :param str metadata: Metadata for the transform.
        :param int target_set_id: The new transform set ID.
        :rtype: None
        """

        face_pts = metadata.get('face')
        if face_pts is None:
            return

        img = cv2.imread(TransformFile().path(transform_set_path, transform_id,
                                              'jpg'))
        img_height, img_width = img.shape[:2]

        # identify the right and left X values for the mouth crop
        m_right_x = face_pts['mouth_right'][0]
        m_left_x = face_pts['mouth_left'][0]
        mouth_width = m_right_x - m_left_x
        left_x = int(m_left_x - (self._offset_percent * mouth_width / 2))
        right_x = int(m_right_x + (self._offset_percent * mouth_width / 2))
        if left_x < 0:
            left_x = 0
        if right_x > img_width:
            right_x = img_width
        if (right_x - left_x) % 2 != 0:
            right_x -= 1
        
        # identify the upper and lower Y values for the mouth crop
        m_right_y = face_pts['mouth_right'][1]
        m_left_y = face_pts['mouth_left'][1]
        mouth_height = abs(m_right_y - m_left_y)
        if mouth_height % 2 != 0:
            mouth_height -= 1

        crop_mouth_height = (right_x - left_x) - mouth_height

        top_y = int(min(m_right_y, m_left_y) - (crop_mouth_height / 2))
        bottom_y = int(max(m_right_y, m_left_y) + (crop_mouth_height / 2))
        
        # check that we are within frame boundaries
        if top_y < 0:
            top_y = 0
        if bottom_y > img_height:
            bottom_y = img_height

        # guarantee that we extract a square cropping
        while (bottom_y - top_y) > (right_x - left_x):
            if top_y > 0:
                top_y += 1
            elif bottom_y < img_height:
                bottom_y -= 1

        while (bottom_y - top_y) < (right_x - left_x):
            if top_y > 0:
                top_y -= 1
            elif bottom_y < img_height:
                bottom_y += 1
    
        mouth_img = img[top_y:bottom_y, left_x:right_x]

        metadata['mouth'] = {'box': [(left_x, top_y), (right_x, bottom_y)]}
        target_id = TransformModel().insert(target_set_id, frame_id,
                                            json.dumps(metadata), 0)
        output_path = TransformFile.path(
            TransformSetSubDir.path(target_set_id), target_id, 'jpg')
        cv2.imwrite(output_path, mouth_img)
