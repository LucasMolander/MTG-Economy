from prettytable import PrettyTable
from typing import List, Tuple

class PrintUtil(object):
    """
    Houses useful methods for printing info to the user.
    """

    #
    # @param header list of tuples (header, alignment)
    # @param rows list of strings
    #
    @staticmethod
    def getTable(header: List[Tuple[str]], rows: List[List[str]], sortby=None, reversesort=False) -> str:
        columns = [h[0] for h in header]

        t = PrettyTable(columns)

        # Align each column correctly
        for h in header:
            t.align[h[0]] = h[1]

        # Add the rows
        for row in rows:
            t.add_row(row)

        # Sort, potentially
        if (sortby is not None):
            t.sortby = sortby
            t.reversesort = reversesort

        # t.set_style(float_format=".2")
        # t.float_format['%'] = '.2'
        t.float_format = '.2'

        return t.get_string()