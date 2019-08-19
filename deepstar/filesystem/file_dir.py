import os


class FileDir:
    """
    This class implements the FileDir class.
    """

    @classmethod
    def path(cls):
        """
        This method returns the path to the file directory.

        :rtype: str
        """

        return os.path.join(
            os.path.realpath(os.environ['DEEPSTAR_PATH']),
            'files'
        )

    @classmethod
    def init(cls):
        """
        This method initializes the file directory.

        :rtype: None
        """

        os.makedirs(FileDir.path(), exist_ok=True)
