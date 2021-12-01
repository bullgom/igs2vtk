from collections import namedtuple
from typing import List
from ..iges import Iges
from .section_reader import SectionReader, IgesLine

class StartSectionReader(SectionReader):
    """
    Reader for the 'Start' section.
    Start section contains human readable description of the file.
    """

    def __init__(self):
        super().__init__()

    def read_line(self, line: IgesLine):
        """
        Example
        ------
        >>> start_reader = StartSectionReader(Iges())
        >>> line = IgesLine("INTEGRATED CIRCUIT SEMICUSTOM CELL (ONE PART OF A LIBRARY FILE)", "S", "1")
        >>> start_reader.read_line(line)
        >>> start_reader.unit_buffer
        'INTEGRATED CIRCUIT SEMICUSTOM CELL (ONE PART OF A LIBRARY FILE)'
        """
        self.unit_buffer += line.content

    def process_unit(self, sequence: int):
        """
        Appends the content of the line to iges's description

        Examples
        ------
        >>> start_reader = StartSectionReader(Iges())
        >>> line = IgesLine("INTEGRATED CIRCUIT SEMICUSTOM CELL (ONE PART OF A LIBRARY FILE)", "S", "1")
        >>> start_reader.read_line(line)
        >>> start_reader.process_unit()
        >>> start_reader.iges.description
        'INTEGRATED CIRCUIT SEMICUSTOM CELL (ONE PART OF A LIBRARY FILE)'
        >>> start_reader.unit_buffer
        ''
        """
        self.iges.description += self.unit_buffer
        self.reset_unit_buffer()

    def unit_ready(self) -> bool:
        """Same as unit buffer not empty"""
        return self.unit_buffer

    def reset_unit_buffer(self):
        return super().reset_unit_buffer()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
