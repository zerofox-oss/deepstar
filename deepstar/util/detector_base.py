class DetectorBase():
    def video_select_detect(self, video_path, **kwargs):
        """
        Returns True if a deepfake video, False otherwise.

        :param str video_path: The filepath to the video on local disk.
        :rtype: bool
        """

        raise NotImplementedError('Detector.predict not implemented')
