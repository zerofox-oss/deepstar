from deepstar.models.model import Model


class FrameSetModel(Model):
    """
    This class implements the FrameSetModel class.
    """

    @classmethod
    def init(cls):
        """
        This method initializes the model.

        :rtype: None
        """

        query = """
                CREATE TABLE IF NOT EXISTS frame_sets (
                    id INTEGER PRIMARY KEY,
                    video_id INTEGER
                )
                """

        Model.execute(query)

    def select(self, frame_set_id):
        """
        This method performs a select operation.

        :param int frame_set_id: The frame set ID.
        :rtype: tuple
        """

        query = """
                SELECT id, video_id
                FROM frame_sets
                WHERE id = ?
                """

        result = Model.execute(query, (frame_set_id,))

        return result.fetchone()

    def insert(self, video_id):
        """
        This method performs an insert operation.

        :param int video_id: The foreign key video ID.
        :rtype: int
        """

        query = """
                INSERT INTO frame_sets
                (video_id)
                VALUES
                (?)
                """

        result = Model.execute(query, (video_id,))

        return result.lastrowid

    def list(self):
        """
        This method performs a list operation.

        :rtype: tuple
        """

        query = """
                SELECT id, video_id
                FROM frame_sets
                """

        result = Model.execute(query)

        return result.fetchall()

    def delete(self, frame_set_id):
        """
        This method performs a delete operation.

        :param int frame_set_id: The frame set ID.
        :rtype: bool
        """

        query = """
                DELETE
                FROM frame_sets
                WHERE id = ?
                """

        result = Model.execute(query, (frame_set_id,))

        return True if result.rowcount == 1 else False
