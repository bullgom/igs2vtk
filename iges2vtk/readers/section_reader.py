from collections import namedtuple
from typing import List
from ..iges import Iges, PreprocessorData
from abc import ABC, abstractmethod
from dataclasses import dataclass

def chunk_string(string: str, length: int) -> List[str]:
    return [string[y-length:y] for y in range(length, len(string)+length,length)]

@dataclass
class IgesLine:
    content: str
    section: str
    sequence: str


class SectionReader(ABC):
    """
    Base class for a reader.
    Works with units of data since Iges files are mostly in 2 lines.
    """

    def __init__(self, iges: Iges) -> None:
        assert issubclass(type(iges), Iges)
        self.iges: Iges = iges
        self.reset_unit_buffer()

    @abstractmethod
    def read_line(self, line: IgesLine):
        """Receive an IgesLine, parse and buffer it and save as a unit"""
        raise NotImplementedError

    @abstractmethod
    def process_unit(self):
        """When a unit is ready, process it."""
        raise NotImplementedError

    @abstractmethod
    def unit_ready(self) -> bool:
        """Check if a unit is ready"""
        raise NotImplementedError

    @abstractmethod
    def reset_unit_buffer(self):
        """Rest unit buffer"""
        self.unit_buffer: str = ""


class IgesReader:
    pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
