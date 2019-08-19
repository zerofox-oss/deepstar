import os

from deepstar.filesystem.file_dir import FileDir


class VideoDir:
    """
    This class implements the VideoDir class.
    """

    @classmethod
    def path(cls):
        """
        This method returns the path to the video directory.

        :rtype: str
        """

        return os.path.join(FileDir.path(), 'videos')

    @classmethod
    def init(cls):
        """
        This method initializes the video directory.

        :rtype: None
        """

        os.makedirs(VideoDir.path(), exist_ok=True)
