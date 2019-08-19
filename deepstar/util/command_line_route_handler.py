class CommandLineRouteHandler:
    """
    This class implements the CommandLineRouteHandler.
    """

    def usage(self):
        """
        This method specifies an interface for the method.

        :raises: NotImplementedError
        :rtype: None
        """

        raise NotImplementedError()

    def handle(self, args, opts):
        """
        This method specifies an interface for the method.

        :param list(str) args: The list of command line arguments.
        :param dict opts: The dict of options.
        :raises: NotImplementedError
        :rtype: None
        """

        raise NotImplementedError()
