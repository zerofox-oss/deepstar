import os

from ansimarkup import ansiprint as print


def debug(message, level):
    """
    This function conditionally prints to stdout based on the value of the
    DEBUG_LEVEL environment variable as compared to the value of the level
    argument.

    :param str message: The message to conditionally print to stdout.
    :param int level: The debug level (generally expected to be an integer
        between 0 and 5 (0 = silent, 1 = critical, 2 = important, 3 = normal,
        4 = verbose, 5 = maximum verbosity).
    :rtype: None
    """

    if int(float(os.environ.get('DEBUG_LEVEL', 3))) >= level:
        print(message)
