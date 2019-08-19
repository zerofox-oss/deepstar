from deepstar.models.model import Model


class VideoModel(Model):
    """
    This class implements the VideoModel class.
    """

    @classmethod
    def init(cls):
        """
        This method initializes the model.

        :rtype: None
        """

        query = """
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY,
                    uri TEXT,
                    filename TEXT,
                    description TEXT
                )
                """

        Model.execute(query)

    def select(self, video_id):
        """
        This method performs a select operation.

        :param int video_id: The video ID.
        :rtype: tuple
        """

        query = """
                SELECT id, uri, filename, description
                FROM videos
                WHERE id = ?
                """

        result = Model.execute(query, (video_id,))

        return result.fetchone()

    def insert(self, uri, filename, description=None):
        """
        This method performs an insert operation.

        :param str uri: The URI to the video.
        :param str filename: The filename for the video.
        :rtype: int
        """

        query = """
                INSERT INTO videos
                (uri, filename, description)
                VALUES
                (?, ?, ?)
                """

        result = Model.execute(query, (uri, filename, description))

        return result.lastrowid

    def update(self, video_id, uri=None):
        """
        This method performs an update operation.

        :param int video_id: The video ID.
        :param str uri: The URI.
        :rtype: None
        """

        fields = []
        params = ()

        if uri is not None:
            fields.append('uri = ?')
            params += (uri,)

        if len(fields) == 0:
            return False

        params += (video_id,)

        query = f"""
                UPDATE videos
                SET {', '.join(fields)}
                WHERE id = ?
                """

        result = Model.execute(query, params)

        return True if result.rowcount == 1 else False

    def list(self):
        """
        This method performs a list operation.

        :rtype: tuple
        """

        query = """
                SELECT id, uri, filename, description
                FROM videos
                """

        result = Model.execute(query)

        return result.fetchall()

    def delete(self, video_id):
        """
        This method performs a delete operation.

        :param int video_id: The video ID.
        :rtype: bool
        """

        query = """
                DELETE
                FROM videos
                WHERE id = ?
                """

        result = Model.execute(query, (video_id,))

        return True if result.rowcount == 1 else False
