from typing import List
from ..iges import Iges, ENTRY_LENGTH
from ..entity import Entity
from .section_reader import SectionReader, IgesLine, chunk_string


class ParameterSectionReader(SectionReader):
    """
    Parameter data section uses the delimiters specified in the global section to list paramteres for the entity. These delimiters are usually commas to separate parameters and a semi-colon to end the listing. The parameter data section listing starts with the entity type followed by parameter data in columns 4-64. COlumns 65 to 72 contain the Data Entry pointer number, which gives the index of the data entry listing for this entity. The last columns, 73-80 contain the Sequence Number, being P#, similar to the Data Entry section.
    """

if __name__ == "__main__":
    import doctest
    doctest.testmod()
