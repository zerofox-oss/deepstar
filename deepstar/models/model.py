import sqlite3
from threading import Lock

from deepstar.filesystem.db_file import DBFile


class Model:
    """
    This class implements the Model class.
    """

    db = None
    lock = Lock()

    @classmethod
    def init(cls):
        """
        This method initializes the DB connection.

        :rtype: None
        """

        if Model.db is None:
            Model.db = sqlite3.connect(DBFile.path(), isolation_level=None,
                                       check_same_thread=False)

            Model.db.execute('PRAGMA foreign_keys = 1')

    @classmethod
    def execute(cls, query, params=()):
        """
        This method executes a query with parameters.

        :param str query: The query.
        :param tuple params: The parameters.
        :rtype: sqlite3.Cursor
        """

        Model.lock.acquire()

        try:
            result = Model.db.execute(query, params)
        finally:
            Model.lock.release()

        return result

    @classmethod
    def close(cls):
        """
        This method closes the DB connection.

        :rtype: None
        """

        if Model.db:
            Model.db.close()

            Model.db = None
