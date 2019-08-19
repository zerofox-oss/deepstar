import os

from deepstar.filesystem.video_dir import VideoDir


class VideoFile:
    """
    This class implements the VideoFile class.
    """

    @classmethod
    def path(cls, filename):
        """
        This method returns the path to a video file.

        :param str filename: The filename (only) for a video file (e.g.
            'example.mp4').
        :rtype: str
        """

        return os.path.join(
            VideoDir.path(),
            filename
        )
