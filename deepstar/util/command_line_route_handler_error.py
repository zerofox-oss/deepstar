class CommandLineRouteHandlerError(BaseException):
    """
    This class implements the CommandLineRouteHandlerError.
    """

    def __init__(self, message=None):
        """
        This method initializes an instance of the CommandLineRouteHandlerError
        class.

        :param str message: An optional message.
        :rtype: None
        """

        self._message = message

    @property
    def message(self):
        """
        This method returns the value for the message property.

        :rtype: str
        """

        return self._message
