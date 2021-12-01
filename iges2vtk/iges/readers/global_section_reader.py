from collections import namedtuple
from typing import List, Tuple
from ..iges import Iges, PreprocessorData
from .section_reader import SectionReader, IgesLine

COMMA = ","
H = "H"
UNIT_ENDS = [COMMA, H]
class GlobalSectionReader(SectionReader):
    """
    Reader for the 'Global' section.
    Global section contains preprocessor data.
    It also must be present in the file and end with the G000000# format.
    Strings are expressed in 'Hollerith' format, meaning every string has the
    number of characters it contains followed by an H directly preceding it.

    Example
    ------
    >>> global_reader = GlobalSectionReader(Iges())
    >>> line = IgesLine("1H,,1H;,10H5MICRONLIB,5HPADIN,9HEXAMPLE 1,4HHAND,16,38,06,38,13,", "G","1")
    >>> global_reader.unit_ready()
    False
    >>> global_reader.read_line(line)
    >>> global_reader.unit_buffer
    [',', ';', '5MICRONLIB', 'PADIN', 'EXAMPLE 1', 'HAND', 16.0, 38.0, 6.0, 38.0, 13.0]
    >>> global_reader.left_over
    ''
    >>> global_reader.unit_ready()
    True
    >>> global_reader.process_unit()
    >>> global_reader.unit_buffer
    []
    >>> global_reader.iges.preprocessor_datas
    [',', ';', '5MICRONLIB', 'PADIN', 'EXAMPLE 1', 'HAND', 16.0, 38.0, 6.0, 38.0, 13.0]

    """


    def __init__(self) -> None:
        super().__init__()
        self.reset_left_over()

    def read_line(self, line: IgesLine):
        # A unit ends in either ',' or 'H'

        content = (self.left_over + line.content).strip()
        if content[-1] == ";":
            content = content.replace(";",",")
        self.reset_left_over()

        i = 0
        while i < len(content):
            data_type, length = self.identify_data(content[i:])

            if data_type == COMMA:
                # It's a numerical data
                i = self.parse_numerical(i, length, content)
            else:
                # It's a string data
                i = self.parse_string(i, length, content)
            i += 1

    @staticmethod
    def identify_data(remaining_line: str) -> Tuple[str, int]:
        """
        1. Identify type of next data
            H: string
            ,: int
        2. Identify length of next data
        By counting number of strings until ',' or 'H' is met
        """
        length = 0
        # UNIT_ENDS = [",", "H"] replaced for numba accel.
        while remaining_line[length] not in [",", "H"]: 
            length += 1
        data_type = remaining_line[length]
        
        return data_type, length

    def parse_numerical(self, i: int, length: int, content: str) -> int:
        """Parse a numerical data and return the index to look at"""
        string = content[i:i+length]
        data = float(string) if string else float()
        self.unit_buffer.append(data)
        i += length
        return i

    def parse_string(self, i: int, length: int, content: str) -> int:
        """Parse a string data and return the index to look at"""
        string_length = int(content[i: i+length])
        # length: length of the 'String length'
        # 1: length of 'H'
        
        data_end = i + length + string_length + 1
        if data_end > len(content):
            self.left_over = content[i:data_end]
            i = len(content)
        else:
            i += length + 1
            self.unit_buffer.append(str(content[i:data_end]))
            i = data_end
        return i

    def process_unit(self, sequence: int):
        self.iges.global_data_list += self.unit_buffer
        self.reset_unit_buffer()

    def unit_ready(self) -> bool:
        return len(self.unit_buffer) > 0

    def reset_unit_buffer(self):
        self.unit_buffer: List[PreprocessorData] = []

    def reset_left_over(self):
        self.left_over : str = ""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
