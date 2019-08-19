import os
import shutil

from deepstar.filesystem.db_dir import DBDir
from deepstar.filesystem.file_dir import FileDir
from deepstar.util.command_line_route_handler import CommandLineRouteHandler
from deepstar.util.debug import debug


class ImplodeCommandLineRouteHandler(CommandLineRouteHandler):
    """
    This class implements the ImplodeCommandLineRouteHandler class.
    """

    def implode(self):
        """
        This method implodes the deepstar path including delete the DB and all
        files.

        :rtype: None
        """

        q = f'Are you sure you want to implode the deepstar path ' \
            f'{os.environ["DEEPSTAR_PATH"]} [y/n]? '
        y = 'The deepstar path was succesfully imploded'
        n = 'The deepstar path was not imploded'

        if input(q).strip() == 'y':
            for path in [DBDir.path(), FileDir.path()]:
                shutil.rmtree(path)

            debug(y, 3)
        else:
            debug(n, 3)

    def usage(self):
        """
        This method prints usage.

        :rtype: None
        """

        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'implode_command_line_route_handler_usage.txt')

        with open(path, 'r') as file_:
            usage = file_.read()

        usage = usage.strip()

        debug(usage, 3)

    def handle(self, args, opts):
        """
        This method handles command line arguments for imploding the deepstar
        path.

        :param list(str) argv: The list of command line arguments.
        :param dict opts: The dict of options.
        :rtype: None
        """

        if args[1] == 'implode':
            self.implode()
        elif args[1] == 'usage':
            self.usage()
