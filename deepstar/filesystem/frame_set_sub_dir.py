import os

from deepstar.filesystem.frame_set_dir import FrameSetDir


class FrameSetSubDir:
    """
    This class implements the FrameSetSubDir class.
    """

    @classmethod
    def path(cls, frame_set_id):
        """
        This method returns the path to a frame set sub directory.

        :param int frame_set_id: The frame set ID.
        :rtype: str
        """

        return os.path.join(FrameSetDir.path(), f'{frame_set_id:08X}')
