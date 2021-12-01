from typing import List, Optional, Union
from .section_reader import SectionReader, IgesLine, read_hollerith
from ...common import Pointer


class ParameterSectionReader(SectionReader):
    """
    Parameter data section uses the delimiters specified in the global section to list paramteres for the entity. These delimiters are usually commas to separate parameters and a semi-colon to end the listing. The parameter data section listing starts with the entity type followed by parameter data in columns 4-64. COlumns 65 to 72 contain the Data Entry pointer number, which gives the index of the data entry listing for this entity. The last columns, 73-80 contain the Sequence Number, being P#, similar to the Data Entry section.

    Example
    ------
    >>> preader = ParameterSectionReader(Iges())
    >>> preader.iges.preprocessor_datas += [',', ';']
    >>> e = Entity(type_number=308, pd_pointer=1, structure=0, line_font_pattern=1, level=0, view=0, transformation_matrix_pointer=0, label_display_associativity=0, status_number=20201, line_weight=0, color=0, parameter_line_count=1, form=0, entity_label=' SUBFIG1', subscript=0, parameters=[])
    >>> preader.iges.add_entity(e)
    >>> preader.unit_ready()
    False
    >>> line = IgesLine("308,0,6HPADBLK,4,03,05,07,09;                                         01", "P", "01")
    >>> preader.read_line(line)
    >>> preader.pointer
    0
    >>> preader.unit_ready()
    True
    >>> preader.process_unit()
    >>> preader.iges.entity_dict[0].parameters
    [308.0, 0.0, 'PADBLK', 4.0, 3.0, 5.0, 7.0, 9.0]
    """

    def __init__(self) -> None:
        super().__init__()

    def read_line(self, line: IgesLine):
        content = line.content

        # -1 because the index in file starts at 1 while python index starts at 0
        # /2 because file index points to the sequence number which increases by 2 per entity
        pointer = Pointer(content[64:72].replace(' ', '0'))

        if pointer != self.pointer:
            self.pointer = pointer

        self.line_count += 1

        parameters = content[:64].strip()
        parameters = parameters[:-1]  # last is always delimiter or ending
        self.unit_buffer += parameters.split(self.iges.delimiter)

    def process_unit(self, sequence: int):

        try:

            self.unit_buffer = self.unit_buffer[1:]  # remove entity type

            parameters = [self.convert(entry)
                          for entry in self.unit_buffer if entry != ""]

            entity = self.iges.entity_dict[self.pointer]
            entity.add_parameters(*parameters)
        except KeyError:
            pass

        self.reset_unit_buffer()

    @staticmethod
    def convert(entry: str) -> Union[float, str]:
        i = entry.find("H")

        if i == -1:  # a numerical value
            param = float(entry) if entry else float()

        else:  # a string value
            param = read_hollerith(entry)

        return param

    def unit_ready(self) -> bool:
        try:
            entity = self.iges.entity_dict[self.pointer]
            return entity.parameter_line_count == self.line_count
        except KeyError:
            return True

    def reset_unit_buffer(self):
        self.pointer: Optional[Pointer] = None
        self.unit_buffer: List[str] = []
        self.line_count: int = 0


if __name__ == "__main__":
    import doctest
    doctest.testmod()
