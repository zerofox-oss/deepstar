import os

import cv2
import imutils

from deepstar.filesystem.frame_file import FrameFile
from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir
from deepstar.filesystem.video_file import VideoFile
from deepstar.models.frame_model import FrameModel
from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.video_model import VideoModel
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError
from deepstar.util.debug import debug


class DefaultVideoSelectExtractPlugin:
    """
    This class implements the DefaultVideoSelectExtractPlugin class.
    """

    def video_select_extract(self, video_id, sub_sample=1, max_sample=0):
        """
        This method extracts frames and thumbnails from a video to a frame set.

        :param int video_id: The video ID.
        :param int sub_sample: Sample frames at a rate of 1 sample per
            sub_sample rate. For example, if sub_sample is 30, then sample
            frames at a rate of 1 frame per 30 frames. The default value of 1
            indicates to sample every frame.
        :param int max_sample: Sample up to maximum count of frames. For
            example, sample up to 1000 total frames (and then cease to sample).
            The default value of 0 indicates that there is no maximum count of
            frames.
        :raises: CommandLineRouteHandlerError
        :rtype: int
        """

        result = VideoModel().select(video_id)

        p1 = VideoFile.path(result[2])

        vc = cv2.VideoCapture(p1)

        try:
            if not vc.isOpened():
                raise CommandLineRouteHandlerError(
                    f'OpenCV VideoCapture isOpened returned false for {p1}')

            frame_set_id = FrameSetModel().insert(video_id)

            p2 = FrameSetSubDir.path(frame_set_id)

            os.makedirs(p2)

            frame_model = FrameModel()

            sub_sample_ = sub_sample
            max_sample_ = 0

            while True:
                ret, frame = vc.read()
                if not ret:
                    break

                # sub_sample
                if sub_sample_ != sub_sample:
                    sub_sample_ += 1
                    continue
                else:
                    sub_sample_ = 1

                frame_id = frame_model.insert(frame_set_id, 0)

                p3 = FrameFile.path(p2, frame_id, 'jpg')

                cv2.imwrite(p3, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])

                # imutils.resize preserves aspect ratio.
                thumbnail = imutils.resize(frame, width=192, height=192)

                p4 = FrameFile.path(p2, frame_id, 'jpg', '192x192')

                # can adjust jpeg quality thus impacting file size
                cv2.imwrite(p4, thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 100])

                debug(f'Frame with ID {frame_id:08d} and thumbnail extracted '
                      f'to {p3} and {p4}', 4)

                # max_sample
                max_sample_ += 1

                if max_sample > 0:
                    if max_sample_ == max_sample:
                        break
        finally:
            vc.release()

        return frame_set_id
