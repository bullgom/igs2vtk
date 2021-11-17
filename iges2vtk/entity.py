from typing import Dict, List, Optional, Sequence, Union, Tuple
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
    parameters: List[Union[float, str]] = field(default_factory=list)

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

    def add_parameters(self, *args: List[Union[float, str]]):
        self.parameters += args


@dataclass
class CircularArc(Entity):
    """
    Simple circular arc of constant radius. Usually defined with a Transformation Matrix Entity (Type 124).
    """

    def add_parameters(self, *args: List[Union[float, str]]):
        self.z, self.x, self.y, self.x1, self.y1, self.x2, self.y2 = args


@dataclass
class ConicArc(Entity):
    """
    Arc defined by the equation: Axt^2 + Bxtyt + Cyt^2 + Dxt + Eyt + F = 0, with a Transformation Matrix (Entity 124). Can define an ellipse, parabola, or hyperbola.

    The definitions of the terms ellipse, parabola, and hyperbola are given in terms of the quantities Q1,Q2, andQ3. These quantities are:

            |  A   B/2  D/2 |        |  A   B/2 | 
        Q1= | B/2   C   E/2 |   Q2 = | B/2   C  |   Q3 = A + C 
            | D/2  E/2   F  | 
    A parent conic curve is:

    An ellipse if Q2 > 0 and Q1Q3 < 0.
    A hyperbola if Q2 < 0 and Q1 != 0.
    A parabola if Q2 = 0 and Q1 != 0.
    """

    def add_parameters(self, *args: List[Union[float, str]]):
        self.a, self.b, self.c, self.d, self.e, self.f, \
            self.x1, self.y1, self.z1, self.x2, self.y2, self.z2 = args


@dataclass
class Line(Entity):

    def add_parameters(self, *args: Tuple[float]):
        self.x1, self.y1, self.z1, self.x2, self.y2, self.z2 = args


@dataclass
class Point(Entity):

    def add_parameters(self, *args: Tuple[float]):
        self.x, self.y, self.z = args


@dataclass
class Transformation(Entity):

    def add_parameters(self, *args: List[float]):
        self.r11, self.r12, self.r13, self.t1, \
            self.r21, self.r22, self.r23, self.t2, \
            self.r31, self.r32, self.r33, self.t3 = args


@dataclass
class ConicArc(Entity):

    def add_parameters(self, *args: List[Union[float, str]]):
        self.a, self.b, self.c, self.d, self.e, self.f, \
            self.x1, self.y1, self.z1, self.x2, self.y2, self.z2 = args


@dataclass
class RationalBSlipneCurve(Entity):
    """
    Composes analytic curves.
    Form: 0=Determined by data 1=Line 2=Circular arc 3=Eliptic arc 4=Parabolic arc 5=Hyperbolic arc
    """

    def add_parameters(self, *args: List[Union[float, str]]):
        self.K, self.M, self.flag1, self.flag2, self.flag3, self.flag4 \
            = map(lambda x: int(x), args[:7])

        weight_start_idx = 7 + self.K + self.M + 1
        control_start_idx = weight_start_idx + self.K + 1
        etc_start_idx = control_start_idx + 3 * self.K + 3
        knot_range = range(6, weight_start_idx)
        weight_range = range(weight_start_idx, control_start_idx)
        control_range = range(control_start_idx, etc_start_idx)

        self.v0, self.v1, self.xn, self.yn, self.zn = args[etc_start_idx:]

        self.knots = [args[i] for i in knot_range]
        self.weights = [args[i] for i in weight_range]
        self.control_points = [args[i] for i in control_range]


@dataclass
class RationalBSplineSurface(Entity):
    """
    This is a surface entity defined by multiple surfaces. The form number describes the general type: 0=determined from data, 1=Plane, 2=Right circular cylinder, 3=Cone, 4=Sphere, 5=Torus, 6=Surface of revolution, 7=Tabulated cylinder, 8=Ruled surface, 9=General quadratic surface.
    """

    def add_parameters(self, *args: List[Union[float, str]]):
        self.K2, self.K1, self.M1, \
            self.flag1, self.flag2, self.flag3, self.flag4, self.flag5 \
            = map(lambda x: int(x), args[:9])

        knot2_start = 11 + self.K1 + self.M1
        weight_start = 13 + self.K1 + self.M1 + self.K2 + self.M2
        control_start = weight_start + 1 + (1 + self.K1) * (1 + self.K2)
        etc_start = control_start + 9 + 3 * (1 + self.K1) * (1 + self.K2) + 1

        self.knot1 = [args[i] for i in range(9, knot2_start)]
        self.knot2 = [args[i] for i in range(knot2_start, weight_start)]
        self.weights = [args[i] for i in range(weight_start, control_start)]
        self.control_points = [args[i]
                               for i in range(control_start, etc_start)]
        self.U0, self.U1, self.V0, self.V1 = args[etc_start:]


@dataclass
class Face(Entity):
    """
    Defines a bound portion of three dimensional space (R^3) which has a finite area. Used to construct B-Rep Geometries
    """

    def add_parameters(self, *args: List[Union[float, str]]):
        self.pointer = int(args[0])
        self.loop_count = int(args[1])
        self.loop_flag = int(args[2])

        self.loops = [args[i] for i in range(3, 2 + self.loop_count)]


@dataclass
class LoopEdge:
    """Represents edge in a loop. NOT AN ENTITY"""

    type: int
    pointer: int
    index: int
    flag: bool
    curves: List[Tuple[bool, int]]


@dataclass
class Loop(Entity):
    """Defines a loop, specifying a bounded face, for B-Rep Geometries."""

    def add_parameters(self, *args: List[Union[float, str]]):
        self.edge_count = int(args[0])
        self.edges: List[LoopEdge] = []

        edge_idx = 0
        arg_idx = 1
        while edge_idx < self.edge_count:
            edge_type = int(args[arg_idx])
            edge_list_pointer = int(args[arg_idx + 1])
            edge_index = int(args[arg_idx + 2])
            flag = bool(args[arg_idx + 3])
            curve_count = int(args[arg_idx + 4])
            arg_idx += 5

            curves = []
            for i in range(curve_count):
                iso = bool(args[arg_idx])
                psc = int(args[arg_idx + 1])
                curves.append((iso, psc))
                arg_idx += 2

            edge = LoopEdge(edge_type, edge_list_pointer,
                            edge_index, flag, curves)
            self.edges.append(edge)

            edge_idx += 1


@dataclass
class Edge:
    curve: int
    start_vertex_list: int
    start_vertex_index: int
    end_vertex_list: int
    end_vertex_index: int


@dataclass
class EdgeList(Entity):

    def add_parameters(self, *args: List[Union[float, str]]):
        edge_count = int(args[0])

        edge_index = 0
        arg_index = 1
        self.edges: List[Edge] = []

        while edge_index < edge_count:
            e = Edge(*map(lambda x: int(x), args[arg_index:arg_index+5]))
            self.edges.append(e)

            arg_index += 5
            edge_index += 1


@dataclass
class Vertex:
    x: float
    y: float
    z: float


@dataclass
class VertexList(Entity):

    def add_parameters(self, *args: List[Union[float, str]]):
        vertex_count = int(args[0])

        vertex_index = 0
        arg_index = 1
        self.vertices: List[Vertex] = []

        while vertex_index < vertex_count:
            v = Vertex(*args[arg_index: arg_index + 3])
            self.vertices.append(v)
            arg_index += 3
            vertex_index += 1
