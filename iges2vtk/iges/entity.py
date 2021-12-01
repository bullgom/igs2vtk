from typing import ClassVar, Dict, List, Optional, Sequence, Union, Tuple, Any, Type
from dataclasses import dataclass, field
import numpy as np
from pygmsh.common import bspline
from ..common import Pointer
from pygmsh.geo import Geometry
from math import ceil, floor, sqrt
from geomdl import BSpline
import gmsh  # To do some low level creation

"""
NM: Abbreviation for 'not mine'. Used to denote codes that are took from pyiges
"""

"""
Omitted entity type list
202: Angular Dimension Entity, 
210: General Label Entity, 212: General Note Entity, 214: Leader Arrow Entity, 
216: Linear Dimension Entity, 218: Ordimate Dimension Entity, 
"""

Parameter = Union[str, float]


@dataclass
class Entity:
    type_number: int
    # parameter data pointer
    pd_pointer: int
    structure: int
    line_font_pattern: int
    level: int
    view: int
    transformation_pointer: int
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
    parameters: List[Parameter] = field(default_factory=list)

    _geometry: Optional[Any] = None
    _render: ClassVar[bool] = True

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

    def add_parameters(self, *args: List[Parameter]):
        self.parameters += args

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        """Transforms this entity into a vtk object"""
        raise NotImplementedError

    def to_vtk_operator(self) -> Any:
        """
        Transforms this entity into a vtk operator.
        Not an actual object itself, but used to manipulate other vtk objects.
        """
        raise NotImplementedError


@dataclass
class Point(Entity):  # 116

    def add_parameters(self, *args: Tuple[float]):
        self.pos = np.array(args[:3])

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return
        _point = self.pos

        if self.transformation_pointer:
            T = entities[self.transformation_pointer]
            point = T.transform(_point.T)
        else:
            point = _point

        geometry.add_point(point)


@dataclass
class Line(Entity):  # 110

    def add_parameters(self, *args: Tuple[float]):
        self.start = args[:3]
        self.end = args[3:6]

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return

        point1 = np.array(self.start)
        point2 = np.array(self.end)

        if self.transformation_pointer:
            transformation = entities[self.transformation_pointer]
            point1 = transformation.transform(point1)
            point2 = transformation.transform(point2)

        point1 = geometry.add_point(point1, lcar)
        point2 = geometry.add_point(point2, lcar)

        self._geometry = geometry.add_line(point1, point2)


@dataclass
class CopiousData(Entity):  # 106
    """
    Definition of set of points. Type specifies 1: couples, 2: triples, 3: sextuplets

    if type is 1, then 2nd parameter is the common z value for all the other
    xy pairs
    """

    TYPE2PARSE_LENGTH = {1: 2, 2: 3, 3: 6}

    def add_parameters(self, *args: List[Parameter]):
        self.tuple_type: int = int(args[0])

        if self.tuple_type == 1:  # couples
            self.common_z = args[1]
            coordinates = args[2:]
        else:
            self.common_z = None
            coordinates = args[1:]

        length = self.TYPE2PARSE_LENGTH[self.tuple_type]
        self.point_list: List[List] = self.parse_tuple(coordinates, length)

    def parse_tuple(self, args: List[Parameter], length: int) -> List[Tuple]:
        tuple_list: List[List] = []

        # /2 because 2 floats in a couple
        if self.common_z:
            for tuple_idx in range(int(len(args)/length)):
                start = tuple_idx*length
                end = (tuple_idx+1)*length
                tuple_list.append(
                    [*args[start: end], self.common_z])

        else:
            for tuple_idx in range(int(len(args)/length)):
                start = tuple_idx*length
                end = (tuple_idx+1)*length
                tuple_list.append(args[start: end])

        return tuple_list

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return
        """
        Not a mesh, so this can be discarded
        """
        for tuple_point in self.point_list:
            geometry.add_point(tuple_point)


@dataclass
class CircularArc(Entity):  # 100
    """
    Simple circular arc of constant radius. Usually defined with a Transformation Matrix Entity (Type 124).
    """

    def add_parameters(self, *args: List[Parameter]):
        self.z, self.x, self.y, self.x1, self.y1, self.x2, self.y2 = args[:7]

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return

        start = np.array([self.x1, self.y1, self.z])
        end = np.array([self.x2, self.y2, self.z])
        center = np.array([self.x, self.y, self.z])

        if self.transformation_pointer:
            transfomation = entities[self.transformation_pointer]

            start = transfomation.transform(start)[0]
            end = transfomation.transform(end)[0]
            center = transfomation.transform(center)[0]

        start = geometry.add_point(start, lcar)
        end = geometry.add_point(end, lcar)
        center = geometry.add_point(center, lcar)

        geometry.add_circle_arc(start, center, end)


@dataclass
class ConicArc(Entity):  # 124
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

    +@ from https://en.wikipedia.org/wiki/Matrix_representation_of_conic_sections
    center: 
    |xc| = | (BE - 2CD)/(4AC - B^2) |
    |yc| = | (DB - 2AE)/(4AC - B^2) |
    """

    def add_parameters(self, *args: List[Parameter]):
        self.a, self.b, self.c, self.d, self.e, self.f, \
            self.x1, self.y1, self.z1, self.x2, self.y2, self.z2 = args[:12]

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return

        start = np.array([self.x1, self.y1, self.z1])
        end = np.array([self.x2, self.y2, self.z2])
        center = np.array([0, 0, 0])

        a = self.get_major_raidus(
            self.a, self.b, self.c, self.d, self.e, self.f)
        point_on_major = np.array([a, 0, 0])

        if self.transformation_pointer:
            t = entities[self.transformation_pointer]

            start = t.transform(start)[0]
            end = t.transform(end)[0]
            center = t.transform(center)[0]
            point_on_major = t.transform(point_on_major)[0]

        start = geometry.add_point(start, lcar)
        end = geometry.add_point(end, lcar)
        center = geometry.add_point(center, lcar)
        point_on_major = geometry.add_point(point_on_major, lcar)

        geometry.add_ellipse_arc(start, center, point_on_major, end)

    @staticmethod
    def get_x_range(start_pos: np.ndarray, end_pos: np.ndarray, step: float) -> np.ndarray:

        pos = np.arange(start=start_pos[0], stop=end_pos[0]+step, step=step)
        neg = np.array([x * -1 for x in np.flip(pos)])
        return np.hstack((neg, pos))

    @staticmethod
    def get_major_raidus(a, b, c, d, e, f) -> np.float:
        """
        For an ellipse or hyperbola, you can find the canonical form 
        from the general form. 
        We only need `a`, the major radius so `b` is not calculated
        Reference: https://en.wikipedia.org/wiki/Conic_section#Matrix_notation 
        """
        sol = np.array([[a, b/2], [b/2, c]])
        conic_matrix = np.array([[a, b/2, d/2], [b/2, c, e/2], [d/2, e/2, f]])

        eig = np.linalg.eigvals(sol)
        l1, l2 = eig  # lambda 1 and lambda 2
        S = np.linalg.det(conic_matrix)

        canonical_a = -S/(l1**2 * l2)
        return canonical_a

    @staticmethod
    def get_y_positive(a, b, c, d, e, f, x) -> Tuple[float, float]:
        """
        Solve general form for `x`. Given x calculate y the positive version.
        Equations found using `sympy solve`.
        """
        y_positive = (-b*x - d + sqrt(-4*a*c*x**2 - 4*a*e*x -
                                      4*a*f + b**2*x**2 + 2*b*d*x + d**2))/(2*a)

        return y_positive

    @staticmethod
    def get_y_negative(a, b, c, d, e, f, x) -> Tuple[float, float]:
        y_negative = -(b*x + d + sqrt(-4*a*c*x**2 - 4*a*e*x -
                                      4*a*f + b**2*x**2 + 2*b*d*x + d**2))/(2*a)

        return y_negative


@dataclass
class Transformation(Entity):  # 124
    """
    new E = RE + T (E: Entity coordinate)

        | r11 r12 r13 |       | T1 |
    R = | r21 r22 r23 |   T = | T2 |
        | r31 r32 r33 |       | T3 |

    """

    def add_parameters(self, *args: List[float]):
        r11, r12, r13, t1, \
            r21, r22, r23, t2, \
            r31, r32, r33, t3 = (args[:12])

        self.r = np.array([[r11, r12, r13],
                           [r21, r22, r23],
                           [r31, r32, r33]])
        self.t = np.array([[t1, t2, t3]])

    def transform(self, coordinate: np.array) -> np.array:

        return self.r.dot(coordinate) + self.t

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return
        # does nothing by itself
        pass


@dataclass
class SubfigureDefinition(Entity):  # 308

    def add_parameters(self, *args: List[Parameter]):
        self.depth = int(args[0])
        self.name = args[1]
        self.length = int(args[2])
        self.figures = [int(pointer) for pointer in args[3:]]

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return

        if self.transformation_pointer:
            raise NotImplementedError
        pass


@dataclass
class SingularSubfigureInstance(Entity):  # 408

    def add_parameters(self, *args: List[Parameter]):
        self.pointer = int(args[0])
        self.translation = np.array(args[1:4])
        self.scale_factor = args[4]


@dataclass
class RationalBSplineCurve(Entity):
    """
    Composes analytic curves.
    Form: 0=Determined by data 1=Line 2=Circular arc 3=Eliptic arc 4=Parabolic arc 5=Hyperbolic arc
    """

    def add_parameters(self, *args: List[Parameter]):
        self.K, self.degree, self.flag1, self.flag2, self.flag3, self.flag4 \
            = map(lambda x: int(x), args[:6])

        weight_start_idx = 8 + self.K + self.degree
        control_start_idx = weight_start_idx + self.K + 1
        etc_start_idx = control_start_idx + 3 * self.K + 3
        knot_range = range(6, weight_start_idx)
        weight_range = range(weight_start_idx, control_start_idx)

        self.v0, self.v1, self.xn, self.yn, self.zn = args[etc_start_idx:]

        self.knots = [args[i] for i in knot_range]
        self.weights = [args[i] for i in weight_range]
        temp_control_points = args[control_start_idx:etc_start_idx]
        self.control_points = [temp_control_points[i:i + 3] for i in range(0, len(temp_control_points), 3)]

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return

        curve = BSpline.Curve()
        curve.degree = self.degree
        curve.ctrlpts = self.control_points
        curve.knotvector = self.knots
        curve.delta = lcar

        _points = curve.evalpts

        points = []
        for point in _points:

            if self.transformation_pointer:
                transfomation = entities[self.transformation_pointer]

                point = transfomation.transform(point)[0]

            point = geometry.add_point(point, lcar)
            points.append(point)

        spline = geometry.add_bspline(points)


@dataclass
class RationalBSplineSurface(Entity):
    """
    This is a surface entity defined by multiple surfaces. The form number describes the general type: 0=determined from data, 1=Plane, 2=Right circular cylinder, 3=Cone, 4=Sphere, 5=Torus, 6=Surface of revolution, 7=Tabulated cylinder, 8=Ruled surface, 9=General quadratic surface.

    Takes up most of the time saving.
    """

    def add_parameters(self, *args: List[Parameter]):
        start_idx = 9
        self.k1, self.k2, self.m1, self.m2, \
            self.flag1, self.flag2, self.flag3, self.flag4, self.flag5 \
            = map(lambda x: int(x), args[:start_idx])

        knot2_start = start_idx + self.k2 + self.m1 + 2
        weight_start = knot2_start + self.k1 + self.m2 + 2
        self.knot1 = args[start_idx: knot2_start]
        self.knot2 = args[knot2_start: weight_start]

        weight_count = (self.k2 + 1) * (self.k1 + 1)
        control_start = weight_start + weight_count
        self.weights = args[weight_start: control_start]

        etc_start = control_start + 3 * weight_count

        self.control_points: List[List] = []

        i = control_start
        while i < etc_start:
            self.control_points.append(np.array(args[i: i+3]))
            i += 3

        self.control_points = np.array(
            self.control_points).reshape(self.k2+1, self.k1 + 1, 3)

        self.U0, self.U1, self.V0, self.V1 = args[etc_start:]

        assert len(self.knot1) == (2 + self.k2 + self.m1)
        assert len(self.knot2) == (2 + self.k1 + self.m2)
        assert len(self.weights) == weight_count
        assert self.control_points.size == (weight_count * 3)

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return

        rows, cols, z = self.control_points.shape
        # The id have to match, not just coordinates
        top = []
        for i in range(0, cols):
            point = self.control_points[0, i]
            top.append(geometry.add_point(point, lcar))
        top_spline = geometry.add_bspline(top)

        right = [top[-1]]
        for i in range(1, rows):
            point = self.control_points[i, cols-1]
            right.append(geometry.add_point(point, lcar))
        right_spline = geometry.add_bspline(right)

        bottom = [right[-1]]
        for i in range(cols-2, -1, -1):
            point = self.control_points[rows-1, i]
            bottom.append(geometry.add_point(point, lcar))
        bottom_spline = geometry.add_bspline(bottom)

        left = [bottom[-1]]
        for i in range(rows-2, 0, -1):
            point = self.control_points[i, 0]
            left.append(geometry.add_point(point, lcar))
        left.append(top[0])
        left_spline = geometry.add_bspline(left)

        loop = geometry.add_curve_loop(
            [top_spline, right_spline, bottom_spline, left_spline])
        surface = geometry.add_surface(loop)


@dataclass
class Face(Entity):
    """
    Defines a bound portion of three dimensional space (R^3) which has a finite area. Used to construct B-Rep Geometries
    """

    def add_parameters(self, *args: List[Parameter]):
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

    def add_parameters(self, *args: List[Parameter]):
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

    def add_parameters(self, *args: List[Parameter]):
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

    def add_parameters(self, *args: List[Parameter]):
        vertex_count = int(args[0])

        vertex_index = 0
        arg_index = 1
        self.vertices: List[Vertex] = []

        while vertex_index < vertex_count:
            v = Vertex(*args[arg_index: arg_index + 3])
            self.vertices.append(v)
            arg_index += 3
            vertex_index += 1


@dataclass
class SurfaceOfRevolution(Entity):  # 120

    def add_parameters(self, *args: List[Parameter]):
        self.axis_line = Pointer(args[0])
        self.target = Pointer(args[1])
        self.start_angle, self.end_angle = args[2:4]  # radian

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return
        line = entities[self.axis_line]
        target = entities[self.target]
        if not target._geometry:
            # this entity is dependent on another entity,
            # if the other entity is not rendered, this will not work
            # so enable it for this
            old_render = target._render
            target._render = True
            target.to_vtk(entities, geometry, lcar)
            target._render = old_render
        target_geometry = target._geometry

        geometry.revolve(target_geometry, line.start, line.end, 3.14)


@dataclass
class CompositeCurve(Entity):  # 102

    def add_parameters(self, *args: List[Parameter]):
        curve_count = int(args[0])
        self.curves: List[Pointer] = list(map(Pointer, args[1:]))

    def to_vtk(self, entities: Dict[Pointer, "Entity"], geometry: Geometry, lcar: float = 0.1):
        if not self._render:
            return


# todo
# Surface Revolution Type 120
# Composite Curve 102
# Trimmed Surface 144
# Curve on Parametric Surface 142
