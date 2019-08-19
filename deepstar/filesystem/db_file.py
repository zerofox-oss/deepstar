import os

from deepstar.filesystem.db_dir import DBDir


class DBFile:
    """
    This class implements the DBFile class.
    """

    @classmethod
    def path(cls):
        """
        This method returns the path to the db file.

        :rtype: str
        """

        return os.path.join(DBDir.path(), 'deepstar.sqlite3')
