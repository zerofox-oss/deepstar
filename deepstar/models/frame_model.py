from deepstar.models.model import Model
from deepstar.models.frame_set_model import FrameSetModel


class FrameModel(Model):
    """
    This class implements the FrameModel class.
    """

    @classmethod
    def init(cls):
        """
        This method initializes the model.

        :rtype: None
        """

        query = """
                CREATE TABLE IF NOT EXISTS frames (
                    id INTEGER PRIMARY KEY,
                    fk_frame_sets INTEGER,
                    rejected INTEGER,
                    FOREIGN KEY(fk_frame_sets) REFERENCES frame_sets(id)
                        ON DELETE CASCADE
                )
                """

        Model.execute(query)

    def select(self, frame_id):
        """
        This method performs a select operation.

        :param int frame_id: The frame ID.
        :rtype: tuple
        """

        query = """
                SELECT id, fk_frame_sets, rejected
                FROM frames
                WHERE id = ?
                """

        result = Model.execute(query, (frame_id,))

        return result.fetchone()

    def insert(self, frame_set_id, rejected):
        """
        This method performs an insert operation.

        :param int frame_set_id: The frame set ID.
        :param int rejected: 1 or 0 for rejected or not rejected respectively.
        :rtype: int
        """

        query = """
                INSERT INTO frames
                (fk_frame_sets, rejected)
                VALUES
                (?, ?)
                """

        result = Model.execute(query, (frame_set_id, rejected))

        return result.lastrowid

    def list(self, frame_set_id, length=-1, offset=None, rejected=True):
        """
        This method performs a list operation.

        :param int frame_set_id: The frame set ID.
        :param int length: The optional length.
        :param int offset: The optional offset.
        :param bool rejected: True if should include rejected frames else False
            if should not. The defalut value is True.
        :rtype: tuple
        """

        result = FrameSetModel().select(frame_set_id)
        if result is None:
            return None

        params = (frame_set_id,)

        query = """
                SELECT id, fk_frame_sets, rejected
                FROM frames
                WHERE fk_frame_sets = ?
                """

        if rejected is False:
            query += ' AND rejected = 0'

        if length is not None:
            query += ' LIMIT ?'
            params += (length,)

        if offset is not None:
            query += ' OFFSET ?'
            params += (offset,)

        result = Model.execute(query, params)

        return result.fetchall()

    def update(self, frame_id, rejected):
        """
        This method performs an update operation.

        :param int frame_id: The frame ID.
        :param int rejected: 1 or 0 for rejected or not rejected respectively.
        :rtype: None
        """

        query = """
                UPDATE frames
                SET rejected = ?
                WHERE id = ?
                """

        result = Model.execute(query, (rejected, frame_id))

        return True if result.rowcount == 1 else False

    def count(self, frame_set_id, rejected=True):
        """
        This method performs a count operation.

        :param int frame_set_id: The frame set ID.
        :param bool rejected: True if should include rejected frames else False
            if should not. The default value is True.
        :rtype: int
        """

        params = (frame_set_id,)

        query = """
                SELECT count(*)
                FROM frames
                WHERE fk_frame_sets = ?
                """

        if rejected is False:
            query += ' AND rejected = 0'

        result = Model.execute(query, params)

        return result.fetchone()[0]
