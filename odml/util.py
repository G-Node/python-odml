# -*- coding: utf-8
"""
Module containing general utility functions.
"""


def format_cardinality(in_val):
    """
    Checks an input value and formats it towards a custom tuple format
    used in odml Section, Property and Values cardinality.

    The following cases are supported:
    (n, n) - default, no restriction
    (d, n) - minimally d entries, no maximum
    (n, d) - maximally d entries, no minimum
    (d, d) - minimally d entries, maximally d entries

    Only positive integers are supported. 'None' is used to denote
    no restrictions on a maximum or minimum.

    :param in_val: Can either be 'None', a positive integer, which will set
                   the maximum or an integer 2-tuple of the format '(min, max)'.

    :returns: None or the value as tuple. A ValueError is raised, if the
              provided value was not in an acceptable format.
    """
    exc_msg = "Can only assign positive single int or int-tuples of the format '(min, max)'"

    # Empty values reset the cardinality to None.
    if not in_val:
        return None

    # Catch tuple edge cases (0, 0); (None, None); (0, None); (None, 0)
    if isinstance(in_val, (tuple, list)) and len(in_val) == 2 and not in_val[0] and not in_val[1]:
        return None

    # Providing a single integer sets the maximum value in a tuple.
    if isinstance(in_val, int) and in_val > 0:
        return None, in_val

    # Integer 2-tuples of the format '(min, max)' are supported to set the cardinality.
    # Also support lists with a length of 2 without advertising it.
    if isinstance(in_val, (tuple, list)) and len(in_val) == 2:
        v_min = in_val[0]
        v_max = in_val[1]

        min_int = isinstance(v_min, int) and v_min >= 0
        max_int = isinstance(v_max, int) and v_max >= 0

        if max_int and min_int and v_max >= v_min:
            return v_min, v_max

        if max_int and not v_min:
            return None, v_max

        if min_int and not v_max:
            return v_min, None

        # Use helpful exception message in the following case:
        if max_int and min_int and v_max < v_min:
            exc_msg = "Minimum larger than maximum (min=%s, max=%s)" % (v_min, v_max)

    raise ValueError(exc_msg)
