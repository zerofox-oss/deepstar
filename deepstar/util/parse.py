def parse_range(range_):
    """
    This function parses a range.

    Example:

    '1-3,5,7-9' -> [1, 2, 3, 5, 7, 8, 9]

    :param str range: The range.
    :rtype: list(int)
    """

    result = []

    range_ = range_.replace(' ', '')

    for a in range_.split(','):
        b = a.split('-')

        if len(b) == 1:
            result.append(int(b[0]))
        else:
            for x in range(int(b[0]), int(b[1]) + 1):
                result.append(x)

    return result
