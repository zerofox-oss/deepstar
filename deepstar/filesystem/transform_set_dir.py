import os

from deepstar.filesystem.file_dir import FileDir


class TransformSetDir:
    """
    This class implements the TransformSetDir class.
    """

    @classmethod
    def path(cls):
        """
        This method returns the path to the transform set directory.

        :rtype: str
        """

        return os.path.join(FileDir.path(), 'transform_sets')

    @classmethod
    def init(cls):
        """
        This method initializes the transform set directory.

        :rtype: None
        """

        os.makedirs(TransformSetDir.path(), exist_ok=True)
