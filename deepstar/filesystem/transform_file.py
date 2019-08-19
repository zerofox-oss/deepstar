import os


class TransformFile:
    """
    This class implements the TransformFile class.
    """

    @classmethod
    def name(cls, transform_id, extension):
        """
        This method formats the transform file's name.

        :param int transform_id: The transform ID.
        :param str extension: The transform file's file extension (e.g. 'jpg').
        :rtype: str
        """

        return f'{transform_id:08X}.{extension}'

    @classmethod
    def path(cls, transform_set_path, transform_id, extension):
        """
        This method returns the path to the transform file.

        :param str transform_set_path: The path to the transform set directory.
        :param int transform_id: The transform ID.
        :param str extension: The transform file's file extension (e.g. 'jpg').
        :rtype: str
        """

        return os.path.join(
            transform_set_path,
            TransformFile.name(transform_id, extension)
        )
