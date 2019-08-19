import logging

logging.getLogger('tensorflow').setLevel(logging.ERROR)  # noqa

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # noqa

import sys
import textwrap


from deepstar.command_line_route_handlers.frame_command_line_route_handler \
    import FrameCommandLineRouteHandler
from deepstar.command_line_route_handlers \
    .frame_set_command_line_route_handler \
    import FrameSetCommandLineRouteHandler
from deepstar.command_line_route_handlers.implode_command_line_route_handler \
    import ImplodeCommandLineRouteHandler
from deepstar.command_line_route_handlers \
    .transform_command_line_route_handler \
    import TransformCommandLineRouteHandler
from deepstar.command_line_route_handlers \
    .transform_set_command_line_route_handler \
    import TransformSetCommandLineRouteHandler
from deepstar.command_line_route_handlers.video_command_line_route_handler \
    import VideoCommandLineRouteHandler
from deepstar.filesystem.db_dir import DBDir
from deepstar.filesystem.file_dir import FileDir
from deepstar.filesystem.frame_set_dir import FrameSetDir
from deepstar.filesystem.transform_set_dir import TransformSetDir
from deepstar.filesystem.video_dir import VideoDir
from deepstar.models.frame_model import FrameModel
from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.model import Model
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.models.video_model import VideoModel
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError
from deepstar.util.command_line_route_not_found_error import \
    CommandLineRouteNotFoundError
from deepstar.util.command_line_router import CommandLineRouter
from deepstar.util.debug import debug


class Deepstar:
    """
    This class implements the Deepstar class.
    """

    @classmethod
    def init(cls):
        """
        This method initializes the Deepstar environment (filesystem, db, etc).

        :rtype: None
        """

        for cls in [DBDir, FileDir, FrameSetDir, VideoDir, TransformSetDir,
                    Model, VideoModel, FrameSetModel, FrameModel,
                    TransformSetModel, TransformModel]:
            cls.init()

    def usage(self):
        """
        This method prints usage.

        :rtype: None
        """

        usage = textwrap.dedent('''
                <red>Usage - Deepstar</red>

                <red>Videos</red>
                  $ python main.py usage videos

                <red>Frame Sets</red>
                  $ python main.py usage frame_sets

                <red>Frames</red>
                  $ python main.py usage frames

                <red>Transform Sets</red>
                  $ python main.py usage transform_sets

                <red>Transforms</red>
                  $ python main.py usage transforms

                <red>Implode</red>
                  $ python main.py usage implode
                ''').strip()

        debug(usage, 3)

    def main(self, argv=sys.argv):
        """
        This method implements the main entry point.

        :param list(str) argv: The value of sys.argv by default or a list of
            command line arguments otherwise.
        :raises: CommandLineRouteHandlerError, CommandLineRouteNotFoundError
        :rtype: None
        """

        Deepstar.init()

        routes = [
            # videos
            ('^usage videos$', VideoCommandLineRouteHandler),
            ('^insert videos youtube .+$', VideoCommandLineRouteHandler),
            ('^insert videos vimeo .+$', VideoCommandLineRouteHandler),
            ('^insert videos file .+$', VideoCommandLineRouteHandler),
            ('^insert videos image .+$', VideoCommandLineRouteHandler),
            ('^select videos [\\d,\\-]+ extract$',
             VideoCommandLineRouteHandler),
            ('^delete videos [\\d,\\-]+$', VideoCommandLineRouteHandler),
            ('^list videos$', VideoCommandLineRouteHandler),
            ('^select videos \\d+ deploy .+$', VideoCommandLineRouteHandler),
            ('^select videos \\d+ detect .+$', VideoCommandLineRouteHandler),
            # frame_sets
            ('^usage frame_sets$', FrameSetCommandLineRouteHandler),
            ('^insert frame_sets images .+$', FrameSetCommandLineRouteHandler),
            ('^select frame_sets \\d+ curate manual$',
             FrameSetCommandLineRouteHandler),
            ('^select frame_sets [\\d,\\-]+ merge$',
             FrameSetCommandLineRouteHandler),
            ('^select frame_sets [\\d,\\-]+ extract \\S+$',
             FrameSetCommandLineRouteHandler),
            ('^select frame_sets [\\d,\\-]+ clone$',
             FrameSetCommandLineRouteHandler),
            ('^select frame_sets [\\d,\\-]+ export dir .+$',
             FrameSetCommandLineRouteHandler),
            ('^delete frame_sets [\\d,\\-]+$',
             FrameSetCommandLineRouteHandler),
            ('^list frame_sets$', FrameSetCommandLineRouteHandler),
            # frames
            ('^usage frames$', FrameCommandLineRouteHandler),
            ('^list frame_sets \\d+ frames$', FrameCommandLineRouteHandler),
            # transform_sets
            ('^usage transform_sets$', TransformSetCommandLineRouteHandler),
            # curate manual must come before curate .+
            ('^select transform_sets \\d+ curate manual$',
             TransformSetCommandLineRouteHandler),
            # curate .+ must come after curate manual
            ('^select transform_sets [\\d,\\-]+ curate .+$',
             TransformSetCommandLineRouteHandler),
            ('^select transform_sets [\\d,\\-]+ merge$',
             TransformSetCommandLineRouteHandler),
            ('^select transform_sets [\\d,\\-]+ merge .+$',
             TransformSetCommandLineRouteHandler),
            ('^select transform_sets [\\d,\\-]+ extract \\S+$',
             TransformSetCommandLineRouteHandler),
            ('^select transform_sets [\\d,\\-]+ clone$',
             TransformSetCommandLineRouteHandler),
            ('^select transform_sets [\\d,\\-]+ export dir .+$',
             TransformSetCommandLineRouteHandler),
            ('^select transform_sets [\\d,\\-]+ export video .+$',
             TransformSetCommandLineRouteHandler),
            ('^delete transform_sets [\\d,\\-]+$',
             TransformSetCommandLineRouteHandler),
            ('^list transform_sets$', TransformSetCommandLineRouteHandler),
            # transforms
            ('^usage transforms$', TransformCommandLineRouteHandler),
            ('^list transform_sets \\d+ transforms$',
             TransformCommandLineRouteHandler),
            # implode
            ('^usage implode$', ImplodeCommandLineRouteHandler),
            ('^implode$', ImplodeCommandLineRouteHandler)
        ]

        error = False

        try:
            CommandLineRouter().route(routes, argv=argv)
        except CommandLineRouteHandlerError as e:
            debug(e.message, 2)
            error = True
        except CommandLineRouteNotFoundError:
            self.usage()
            error = True

        return 1 if error else 0
