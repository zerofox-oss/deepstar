import os

from deepstar.filesystem.file_dir import FileDir


class FrameSetDir:
    """
    This class implements the FrameSetDir class.
    """

    @classmethod
    def path(cls):
        """
        This method returns the path to the frame set directory.

        :rtype: str
        """

        return os.path.join(FileDir.path(), 'frame_sets')

    @classmethod
    def init(cls):
        """
        This method initializes the frame set directory.

        :rtype: None
        """

        os.makedirs(FrameSetDir.path(), exist_ok=True)
