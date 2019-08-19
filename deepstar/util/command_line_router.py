import re
import sys

from deepstar.util.command_line_route_not_found_error import \
    CommandLineRouteNotFoundError


class CommandLineRouter:
    """
    This class implements the CommandLineRouter class.
    """

    def parse_opt(self, opt):
        """
        This method parses an option into a key value pair. If the option has
        no value then it's value is set to True.

        :param str opt: The option.
        :rtype: str, str|bool
        """

        opt = opt.lstrip('--')

        if '=' in opt:
            k, v = opt.split('=')
        else:
            k, v = (opt, True)

        return k, v

    def parse_argv(self, argv):
        """
        This method parses arguments and options.

        :param list(str) argv: A list of command line arguments.
        :rtype: list(str), dict
        """

        args = []
        opts = {}

        for arg in argv:
            if arg.startswith('-'):
                k, v = self.parse_opt(arg)

                opts[k] = v
            else:
                args.append(arg)

        return args, opts

    def route(self, routes, argv=sys.argv):
        """
        This method routes command line arguments to the appropriate command
        line route handler.

        :param list((str, object)) routes: A list of tuples consisting of a
            regular expression and a class.
        :param list(str) argv: The value of sys.argv by default or a list of
            command line arguments otherwise.
        :raises: CommandLineRouteNotFoundError
        :rtype: None
        """

        args, opts = self.parse_argv(argv)

        for route in routes:
            if re.match(route[0], ' '.join(args[1:])):
                route[1]().handle(args, opts)
                return

        raise CommandLineRouteNotFoundError()
