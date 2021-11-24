from .start_section_reader import StartSectionReader
from .global_section_reader import GlobalSectionReader
from .data_entry_section_reader import DataEntrySectionReader
from .parameter_section_reader import ParameterSectionReader
from .section_reader import IgesLine, Section, SectionReader
from ..iges import Iges
from typing import Dict, TextIO
from tqdm import tqdm
import mpipe as mp

class IgesReader:

    def __init__(self) -> None:
        self.start_reader = StartSectionReader()
        self.global_reader = GlobalSectionReader()
        self.data_reader = DataEntrySectionReader()
        self.param_reader = ParameterSectionReader()

        self.reader_map: Dict[Section, SectionReader] = {
            Section.Start.value: self.start_reader,
            Section.Global.value: self.global_reader,
            Section.Data.value: self.data_reader,
            Section.Parameter.value: self.param_reader
        }

    def distribute_iges(self, iges: Iges):

        for reader in self.reader_map.values():
            reader.iges = iges

    def read_file(self, filename: str) -> Iges:
        iges = Iges()
        self.distribute_iges(iges)
        
        # setup pipeline

        with open(filename, 'r') as file:
            pbar = tqdm()
            while (line := self.parse_line(file)).section != Section.Terminal.value:
                reader = self.reader_map[line.section]
                reader.read_line(line)

                if reader.unit_ready():
                    reader.process_unit()
                pbar.update()
            pbar.close()
        return iges

    def parse_line(self, file: TextIO) -> IgesLine:
        """Read a line from file, convert it to IgesLine"""
        line = file.readline()
        content = line[:72]
        section = line[72]
        sequence_number = int(line[73:-1].replace(' ', '0'))
        iges_line = IgesLine(content, section, sequence_number)
        return iges_line


if __name__ == "__main__":
    filename = "cases/ex1.iges"
    reader = IgesReader()
    iges = reader.read_file(filename)
    print(iges)
