from typing import Dict, List, Optional, Sequence
from dataclasses import dataclass, field


@dataclass
class Entity:
    type_number: int
    # parameter data pointer
    pd_pointer: int
    structure: int
    line_font_pattern: int
    level: int
    view: int
    transformation_matrix_pointer: int
    label_display_associativity: int

    status_number: int
    # instead of using the sequence number, use the index of entity
    # sequence_number: int
    line_weight: int
    color: int
    parameter_line_count: int
    form: int
    entity_label: str
    subscript: int
    # instead of just [], below is required
    # because mutable default is not allowed
    parameters: List[int] = field(default_factory=list)

    @staticmethod
    def parse_status_number(x: str) -> int:
        """
        inputs
            x: A candidate status number in string
        output
            status number in integer
        """
        numbers = x.split(" ")
        numbers = [n.zfill(2) for n in numbers]
        return int("".join(numbers))
