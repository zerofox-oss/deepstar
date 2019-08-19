from deepstar.models.model import Model
from deepstar.models.transform_set_model import TransformSetModel


class TransformModel(Model):
    """
    This class implements the TransformModel class.
    """

    @classmethod
    def init(cls):
        """
        This method initializes the model.

        :rtype: None
        """

        query = """
                CREATE TABLE IF NOT EXISTS transforms (
                    id INTEGER PRIMARY KEY,
                    fk_transform_sets INTEGER,
                    fk_frames INTEGER,
                    metadata TEXT,
                    rejected INTEGER,
                    FOREIGN KEY(fk_transform_sets)
                        REFERENCES transform_sets(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY(fk_frames) REFERENCES frames(id)
                )
                """

        Model.execute(query)

    def select(self, transform_id):
        """
        This method performs a select operation.

        :param int transform_id: The transform ID.
        :rtype: tuple
        """

        query = """
                SELECT id, fk_transform_sets, fk_frames, metadata, rejected
                FROM transforms
                WHERE id = ?
                """

        result = Model.execute(query, (transform_id,))

        return result.fetchone()

    def insert(self, transform_set_id, frame_id, metadata, rejected):
        """
        This method performs an insert operation.

        :param int transform_set_id: The transform set ID.
        :param int frame_id: The frame ID.
        :param str metadata: Metadata from the transform.
        :param int rejected: 1 or 0 for rejected or not rejected respectively.
        :rtype: int
        """

        query = """
                INSERT INTO transforms
                (fk_transform_sets, fk_frames, metadata, rejected)
                VALUES
                (?, ?, ?, ?)
                """

        result = Model.execute(query, (transform_set_id, frame_id, metadata,
                                       rejected))

        return result.lastrowid

    def list(self, transform_set_id, length=-1, offset=None, rejected=True):
        """
        This method performs a list operation.

        :param int transform_set_id: The transform set ID.
        :param int length: The optional length.
        :param int offset: The optional offset.
        :param bool rejected: True if should include rejected transforms else
            False if should not. The default value is True.
        :rtype: tuple
        """

        result = TransformSetModel().select(transform_set_id)
        if result is None:
            return None

        params = (transform_set_id,)

        query = """
                SELECT id, fk_transform_sets, fk_frames, metadata, rejected
                FROM transforms
                WHERE fk_transform_sets = ?
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

    def update(self, transform_id, metadata=None, rejected=None):
        """
        This method performs an update operation.

        :param int transform_id: The transform ID.
        :param str metadata: Metadata from the transform.
        :param int rejected: 1 or 0 for rejected or not rejected respectively.
        :rtype: bool
        """

        fields = []
        params = ()

        if metadata is not None:
            fields.append('metadata = ?')
            params += (metadata,)

        if rejected is not None:
            fields.append('rejected = ?')
            params += (rejected,)

        if len(fields) == 0:
            return False

        params += (transform_id,)

        query = f"""
                UPDATE transforms
                SET {', '.join(fields)}
                WHERE id = ?
                """

        result = Model.execute(query, params)

        return True if result.rowcount == 1 else False

    def count(self, transform_set_id, rejected=True):
        """
        This method performs a count operation.

        :param int transform_set_id: The transform set ID.
        :param bool rejected: True if should include rejected transforms else
            False if should not. The defalut value is True.
        :rtype: int
        """

        params = (transform_set_id,)

        query = """
                SELECT count(*)
                FROM transforms
                WHERE fk_transform_sets = ?
                """

        if rejected is False:
            query += ' AND rejected = 0'

        result = Model.execute(query, params)

        return result.fetchone()[0]
