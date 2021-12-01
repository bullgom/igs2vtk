from .iges.iges import Iges
from tqdm import tqdm
from pygmsh.geo import Geometry
from meshio import Mesh


class Converter:
    
    def __init__(self) -> None:
        pass

    def convert(
        self,
        iges: Iges,
        characteristic_length_min: float = 0.1,
        characteristic_length_max: float = 0.1,
        lcar: float = 0.1
    ) -> Mesh:

        with Geometry() as geo:
            geo.characteristic_length_min = characteristic_length_min
            geo.characteristic_length_max = characteristic_length_max

            for entity in tqdm(iges.entity_dict.values()):
                if not entity._geometry:
                    entity.to_vtk(iges.entity_dict, geo, lcar)

            return geo.generate_mesh()
