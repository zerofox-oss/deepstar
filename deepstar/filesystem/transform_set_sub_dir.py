import os

from deepstar.filesystem.transform_set_dir import TransformSetDir


class TransformSetSubDir:
    """
    This class implements the TransformSetSubDir class.
    """

    @classmethod
    def path(cls, transform_set_id):
        """
        This method returns the path to a transform set sub directory.

        :param int transform_set_id: The transform set ID.
        :rtype: str
        """
        return os.path.join(TransformSetDir.path(), f'{transform_set_id:08X}')
