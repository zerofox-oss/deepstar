from deepstar.models.model import Model


class TransformSetModel(Model):
    """
    This class implements the TransformSetModel class.
    """

    @classmethod
    def init(cls):
        """
        This method initializes the model.

        :rtype: None
        """

        query = """
                CREATE TABLE IF NOT EXISTS transform_sets (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    fk_frame_sets INTEGER,
                    fk_prev_transform_sets INTEGER,
                    FOREIGN KEY(fk_frame_sets) REFERENCES frame_sets(id),
                    FOREIGN KEY(fk_prev_transform_sets)
                        REFERENCES transform_sets(id)
                )
                """

        Model.execute(query)

    def select(self, transform_set_id):
        """
        This method performs a select operation.

        :param int transform_set_id: The transform set ID.
        :rtype: tuple
        """

        query = """
                SELECT id, name, fk_frame_sets, fk_prev_transform_sets
                FROM transform_sets
                WHERE id = ?
                """

        result = Model.execute(query, (transform_set_id,))

        return result.fetchone()

    def insert(self, name, frame_set_id, prev_transform_set_id=None):
        """
        This method performs an insert operation.

        :param str name: The comma separated list of transform names.
        :param int frame_set_id: The frame set ID.
        :param int prev_transform_set_id: The previous transform set ID.
        :rtype: int
        """

        query = """
                INSERT INTO transform_sets
                (name, fk_frame_sets, fk_prev_transform_sets)
                VALUES
                (?, ?, ?)
                """

        result = Model.execute(query, (name, frame_set_id,
                                       prev_transform_set_id))

        return result.lastrowid

    def list(self):
        """
        This method performs a list operation.

        :rtype: tuple
        """

        query = """
                SELECT id, name, fk_frame_sets, fk_prev_transform_sets
                FROM transform_sets
                """

        result = Model.execute(query)

        return result.fetchall()

    def delete(self, transform_set_id):
        """
        This method performs a delete operation.

        :param int transform_set_id: The transform set ID.
        :rtype: bool
        """

        query = """
                DELETE
                FROM transform_sets
                WHERE id = ?
                """

        result = Model.execute(query, (transform_set_id,))

        return True if result.rowcount == 1 else False
