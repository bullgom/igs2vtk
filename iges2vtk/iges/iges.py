from typing import Dict, List, Optional
from .entity import Entity
from ..common import Pointer, PreprocessorData

"""
Reference: https://wiki.eclipse.org/IGES_file_Specification

Supported CAD entities can be found
https://knowledge.autodesk.com/support/autocad/learn-explore/caas/CloudHelp/cloudhelp/2016/ENU/AutoCAD-Core/files/GUID-F61C578E-A246-417F-B826-6FB87BF03EF9-htm.html

"""

# Every entry in iges are 8 in legth
ENTRY_LENGTH = 8


class Iges:

    DEFAULT_DELIMITER = ","
    DEFAULT_ENDING = ";"

    def __init__(self) -> None:
        self.entity_dict: Dict[Pointer, Entity] = {}

        self.description: str = ""
        self.global_data_list: List[PreprocessorData] = []

    def add_entity(self, entity: Optional[Entity], sequence: Pointer):

        if entity is not None:
            self.entity_dict[sequence] = entity

    def get_entity(self, pointer: Pointer) -> Optional[Entity]:

        try:
            return self.entity_dict[pointer]
        except KeyError:
            return None

    @property
    def delimiter(self) -> Optional[str]:
        if (delimiter := self.global_data_list[0:1][0]):
            return delimiter
        else:
            return self.DEFAULT_DELIMITER

    @property
    def ending(self) -> Optional[str]:
        if (ending := self.global_data_list[1:2][0]):
            return ending
        else:
            return self.DEFAULT_ENDING

    @property
    def entities(self) -> List[Entity]:
        return self.entity_dict.values()
