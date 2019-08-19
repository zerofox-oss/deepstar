import os

import cv2
import imutils
import numpy as np
from mtcnn.mtcnn import MTCNN
from keras.models import load_model

from deepstar.util.debug import debug
from deepstar.util.detector_base import DetectorBase


class MesoNetVideoSelectDetectPlugin(DetectorBase):
    """
    This class implements the MesoNetVideoSelectDetectPlugin class.
    """

    name = "mesonet"

    def __init__(self):
        self.face_detector = MTCNN()
        model_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'trained_detectors',
            'mesonet.hdf5')
        self.mesonet = load_model(model_path)
    
    def video_select_detect(self, video_path, opts):
        """
        Runs the MesoNet classifier over the selected video.
        Returns True if the video is a deepfale, False if the
        video is authentic, and None if no analysis could be
        performed.

        :param str video_path: The path on local disk to the video.
        :rtype: bool
        """

        vc = cv2.VideoCapture(video_path)

        face_limit = -1
        if opts.get('face-limit'):
            face_limit = int(opts.get('face-limit'))

        threshold = 0.5
        if opts.get('threshold'):
            threshold = float(opts.get('threshold'))
            if threshold > 1 or threshold < 0:
                threshold = 0.5

        face_set = []
        while face_limit == -1 or len(face_set) < face_limit:
            ret, frame = vc.read()
            if not ret:
                break
            
            face_set.extend(self.get_faces(frame))
        
        if len(face_set) < 10:
            debug('Less than 10 faces were extracted from this video' + 
                  ' - detection is unable to be performed', 2)
            return None

        predictions = self.mesonet.predict(
            x=np.array(face_set),
            batch_size=10,
            verbose=0,
        )
        prediction_mean = np.mean(predictions)

        if prediction_mean > threshold:
            debug(f'Video is a deepfake ({prediction_mean:.04f})', 2)
            return True

        debug(f'Video is authentic ({prediction_mean:.04f})', 2)
        return False

    def get_faces(self, frame, min_confidence=0.9, offset_percent=0.2):
        """
        Extracts the faces from a single frame.

        :param np.array frame: The frame image as a numpy array.
        :param float min_confidence: The minumum confidence level of the face detection.
        :param float offset_perfect: Offset for the extracted face.
        :rtype: list
        """

        faces = []
        results = self.face_detector.detect_faces(frame)

        frame_height, frame_width = frame.shape[:2]

        for r in results:
            if r['confidence'] < min_confidence:
                continue

            x, y, width, height = r['box']

            adjusted_x = int(max(0, x - (0.5 * width * offset_percent)))
            adjusted_y = int(max(0, y - (0.5 * height * offset_percent)))
            t = x + width + (0.5 * width * offset_percent)
            adjusted_right_x = int(min(frame_width, t))
            t = y + height + (0.5 * height * offset_percent)
            adjusted_bottom_y = int(min(frame_height, t))        
            
            face_crop = frame[adjusted_y:adjusted_bottom_y,
                              adjusted_x:adjusted_right_x]

            fc_height, fc_width = face_crop.shape[:2]
            if fc_height >= fc_width and fc_height > 256:
                face_crop = imutils.resize(face_crop, height=256)
            elif fc_width > fc_height and fc_width > 256:
                face_crop = imutils.resize(face_crop, width=256)
            fc_height, fc_width = face_crop.shape[:2]

            img_padded = np.zeros((256, 256, 3), dtype=np.uint8)
            img_padded[:fc_height, :fc_width, :] = face_crop.copy()

            faces.append(img_padded)
        
        return faces
