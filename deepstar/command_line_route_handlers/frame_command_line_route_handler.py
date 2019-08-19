import os

import cv2

from deepstar.filesystem.frame_file import FrameFile
from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir
from deepstar.models.frame_model import FrameModel
from deepstar.models.frame_set_model import FrameSetModel
from deepstar.util.command_line_route_handler import CommandLineRouteHandler
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError
from deepstar.util.debug import debug


class FrameCommandLineRouteHandler(CommandLineRouteHandler):
    """
    This class implements the FrameCommandLineRouteHandler class.
    """

    def list(self, frame_set_id):
        """
        This method lists frames in the frame collection for a frame set.

        :param int frame_set_id: The frame set ID.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        result = FrameSetModel().select(frame_set_id)
        if result is None:
            raise CommandLineRouteHandlerError(
                f'Frame set with ID {frame_set_id:08d} not found')

        frame_model = FrameModel()

        count = frame_model.count(frame_set_id)

        debug(f'{count} results', 3)
        debug('id | fk_frame_sets | rejected | (width | height)', 3)
        debug('------------------------------------------------', 3)

        if count == 0:
            return

        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        offset = 0
        p1 = FrameSetSubDir.path(frame_set_id)

        while True:
            frames = frame_model.list(frame_set_id, length=length,
                                      offset=offset)

            if not frames:
                break

            for frame in frames:
                p2 = FrameFile.path(p1, frame[0], 'jpg')

                height, width, _ = cv2.imread(p2).shape

                debug(f'{frame[0]} | {frame[1]} | {frame[2]} | ({width} | '
                      f'{height})', 3)

            offset += length

    def usage(self):
        """
        This method prints usage.

        :rtype: None
        """

        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'frame_command_line_route_handler_usage.txt')

        with open(path, 'r') as file_:
            usage = file_.read()

        usage = usage.strip()

        debug(usage, 3)

    def handle(self, args, opts):
        """
        This method handles command line arguments for the frame collection.

        :param list(str) argv: The list of command line arguments.
        :param dict opts: The dict of options.
        :rtype: None
        """

        if args[1] == 'list':
            self.list(int(args[3]))
        elif args[1] == 'usage':
            self.usage()
