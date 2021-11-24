from typing import List, Optional, Union
from .entity import Entity
from dataclasses import dataclass

"""
Reference: https://wiki.eclipse.org/IGES_file_Specification

Supported CAD entities can be found
https://knowledge.autodesk.com/support/autocad/learn-explore/caas/CloudHelp/cloudhelp/2016/ENU/AutoCAD-Core/files/GUID-F61C578E-A246-417F-B826-6FB87BF03EF9-htm.html

"""

PreprocessorData = Union[str, int, float]

# Every entry in iges are 8 in legth
ENTRY_LENGTH = 8


class Iges:

    DEFAULT_DELIMITER = ","
    DEFAULT_ENDING = ";"

    def __init__(self) -> None:
        self.entities: List[Entity] = []
        self.description: str = ""
        self.preprocessor_datas: List[PreprocessorData] = []

    @property
    def delimiter(self) -> Optional[str]:
        if (delimiter := self.preprocessor_datas[0:1][0]):
            return delimiter
        else:
            return self.DEFAULT_DELIMITER

    @property
    def ending(self) -> Optional[str]:
        if (ending := self.preprocessor_datas[1:2][0]):
            return ending
        else:
            return self.DEFAULT_ENDING
