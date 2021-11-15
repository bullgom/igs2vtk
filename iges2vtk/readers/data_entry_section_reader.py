from typing import List
from ..iges import Iges, ENTRY_LENGTH
from ..entity import Entity
from .section_reader import SectionReader, IgesLine, chunk_string


class DataEntrySectionReader(SectionReader):
    """
    Contains list of entities. Specified by a D in the 73rd column and lists
    properties about the entity it describes. Each line in this section is split
    into 10 8-character fields, and ach entity is given 2 lines of the section.
    This indicates that every entity has 20 fields in the Entry section.

    Example
    ------
    >>> data_reader = DataEntrySectionReader(Iges())
    >>> line1 = IgesLine("     308      01               1       0               0        00020201","D","01")
    >>> line2 = IgesLine("     308       0               1                         SUBFIG1        ","D","02")
    >>> data_reader.read_line(line1)
    >>> data_reader.unit_ready()
    False
    >>> data_reader.read_line(line2)
    >>> data_reader.unit_ready()
    True
    >>> data_reader.unit_buffer
    ['     308', '      01', '        ', '       1', '       0', '        ', '       0', '        ', '00020201', '     308', '       0', '        ', '       1', '        ', '        ', '        ', ' SUBFIG1', '        ']
    >>> data_reader.process_unit()
    >>> data_reader.unit_buffer
    []
    >>> data_reader.iges.entities
    [Entity(type_number=308, pd_pointer=1, structure=0, line_font_pattern=1, level=0, view=0, transformation_matrix_pointer=0, label_display_associativity=0, status_number=20201, line_weight=0, color=0, parameter_line_count=1, form=0, entity_label=' SUBFIG1', subscript=0, parameters=[])]
    """

    FIELD_COUNT = 15

    def __init__(self, iges: Iges) -> None:
        super().__init__(iges)

    def read_line(self, line: IgesLine):
        content = line.content
        chunks = chunk_string(content, ENTRY_LENGTH)

        self.unit_buffer += chunks

    def process_unit(self):
        """
        Creates entity and appends to iges.
        Examples and the document does not match. It is assumed that
        empty entry means default value of 0
        """

        t = self.unit_buffer

        entity_param = []
        for i, entry in enumerate(t):

            if i in [9, 14, 15]:
                # skip these values
                continue

            elif i == 8:  # status number
                param = Entity.parse_status_number(entry)

            elif i == 16:  # entity label
                param = entry  # a string type

            else:
                filled = entry.replace(' ', '0')
                param = int(filled)

            entity_param.append(param)

        e = Entity(*entity_param)
        self.iges.entities.append(e)
        self.reset_unit_buffer()

    def reset_unit_buffer(self):
        self.unit_buffer: List[str] = []

    def unit_ready(self) -> bool:
        # 20 per each line,
        # where 1 of each line is section code and sequence number, which is
        # not parsed, so 9*2
        return len(self.unit_buffer) >= self.FIELD_COUNT


if __name__ == "__main__":
    import doctest
    doctest.testmod()
