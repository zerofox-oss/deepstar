import os


class DBDir:
    """
    This class implements the DBDir class.
    """

    @classmethod
    def path(cls):
        """
        This method returns the path to the db directory.

        :rtype: str
        """

        return os.path.join(
            os.path.realpath(os.environ['DEEPSTAR_PATH']),
            'db'
        )

    @classmethod
    def init(cls):
        """
        This method initializes the db directory.

        :rtype: None
        """

        os.makedirs(DBDir.path(), exist_ok=True)
