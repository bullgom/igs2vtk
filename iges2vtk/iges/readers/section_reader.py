from collections import namedtuple
from typing import List, Optional, TextIO
from ..iges import Iges, PreprocessorData
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
import numba as nb


def read_hollerith(string: str) -> str:
    """
    Parse a string from a hollerith format.
    Assumes the hollerith format starts at the front of the string.
    """
    i = 0
    while string[i] != "H":
        i += 1
    length = int(string[:i])
    # +1 to skip the "H"
    return string[i+1:i+1+length]


def chunk_string(string: str, length: int) -> List[str]:
    """Splits given string into chunks of given length"""
    return [string[y-length:y] for y in range(length, len(string)+length, length)]

@dataclass
class IgesLine:
    content: str
    section: str
    sequence: int


class Section(Enum):
    """Enum representing each section"""
    Start = "S"
    Global = "G"
    Data = "D"
    Parameter = "P"
    Terminal = "T"


class SectionReader(ABC):
    """
    Base class for a reader.
    Works with units of data since Iges files are mostly in 2 lines.
    """

    def __init__(self) -> None:
        self.iges: Optional[Iges] = None
        self.reset_unit_buffer()

    @abstractmethod
    def read_line(self, line: IgesLine) -> None:
        """Receive an IgesLine, parse and buffer it and save as a unit"""
        raise NotImplementedError

    @abstractmethod
    def process_unit(self) -> None:
        """When a unit is ready, process it."""
        raise NotImplementedError

    @abstractmethod
    def unit_ready(self) -> bool:
        """Check if a unit is ready"""
        raise NotImplementedError

    @abstractmethod
    def reset_unit_buffer(self) -> None:
        """Rest unit buffer"""
        self.unit_buffer: str = ""


if __name__ == "__main__":
    import doctest
    doctest.testmod()
