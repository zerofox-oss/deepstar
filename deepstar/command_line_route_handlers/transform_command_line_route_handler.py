import os

import cv2

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_model import TransformSetModel
from deepstar.util.command_line_route_handler import CommandLineRouteHandler
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError
from deepstar.util.debug import debug


class TransformCommandLineRouteHandler(CommandLineRouteHandler):
    """
    This class implements the TransformCommandLineRouteHandler class.
    """

    def list(self, transform_set_id):
        """
        This method lists transforms in the transform collection for a
        transform set.

        :param int transform_set_id: The transform set ID.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        result = TransformSetModel().select(transform_set_id)
        if result is None:
            raise CommandLineRouteHandlerError(
                f'Transform set with ID {transform_set_id:08d} not found')

        transform_model = TransformModel()

        count = transform_model.count(transform_set_id)

        debug(f'{count} results', 3)
        debug('id | fk_transform_sets | fk_frames | metadata | rejected | '
              '(width | height)', 3)
        debug('-----------------------------------------------------------'
              '----------------', 3)

        if count == 0:
            return

        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        offset = 0
        p1 = TransformSetSubDir.path(transform_set_id)

        while True:
            transforms = transform_model.list(transform_set_id, length=length,
                                              offset=offset)

            if not transforms:
                break

            for transform in transforms:
                p2 = TransformFile.path(p1, transform[0], 'jpg')

                height, width, _ = cv2.imread(p2).shape

                debug(f'{transform[0]} | {transform[1]} | {transform[2]} | '
                      f'{transform[3]} | {transform[4]} | ({width} | '
                      f'{height})', 3)

            offset += length

    def usage(self):
        """
        This method prints usage.

        :rtype: None
        """

        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'transform_command_line_route_handler_usage.txt')

        with open(path, 'r') as file_:
            usage = file_.read()

        usage = usage.strip()

        debug(usage, 3)

    def handle(self, args, opts):
        """
        This method handles command line arguments for the transform
        collection.

        :param list(str) argv: The list of command line arguments.
        :param dict opts: The dict of options.
        :rtype: None
        """

        if args[1] == 'list':
            self.list(int(args[3]))
        elif args[1] == 'usage':
            self.usage()
