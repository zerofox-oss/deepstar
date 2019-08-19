import os


class FrameFile:
    """
    This class implements the FrameFile class.
    """

    @classmethod
    def name(cls, frame_id, extension, res=''):
        """
        This method formats the frame file's name.

        :param int frame_id: The frame ID.
        :param str extension: The frame file's file extension (e.g. 'jpg').
        :param str res: An optional string intended to be appended to the file
            name and to indicate the resolution of the frame.
        :rtype: str
        """

        if res:
            res = f'-{res}'

        return f'{frame_id:08X}{res}.{extension}'

    @classmethod
    def path(cls, frame_set_path, frame_id, extension, res=''):
        """
        This method returns the path to the db file.

        :param str frame_set_path: The path to the frame set directory.
        :param int frame_id: The frame ID.
        :param str extension: The frame file's file extension (e.g. 'jpg').
        :param str res: An optional string intended to be appended to the file
            name and to indicate the resolution of the frame.
        :rtype: str
        """

        return os.path.join(
            frame_set_path,
            FrameFile.name(frame_id, extension, res)
        )
