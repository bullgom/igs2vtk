from iges2vtk.iges.readers.iges_reader import IgesReader
from iges2vtk.converter import Converter
from datetime import datetime
from iges2vtk.iges.entity import *

if __name__ == "__main__":
    start_time = datetime.now()

    Line._render = False
    #Point._render = False
    #RationalBSplineSurface._render = False
    #RationalBSplineCurve._render = False
    #ConicArc._render = False
    #CircularArc._render = False
    CopiousData._render = False
    SurfaceOfRevolution._render = False
    CompositeCurve._render = False

    form = "igs"
    dform = "vtk"
    filename = "PN_ICP System"
    source = f"cases/{form}/{filename}.{form}"
    save_name = f"cases/{dform}/{filename}.{dform}"

    reader = IgesReader()
    converter = Converter()
    print(f"Reading file: {source}")
    iges = reader.read_file(source)
    print(f"Converting")
    vtk = converter.convert(iges, 0.1, 0.1, 1)

    print(f"Writing file: {save_name}")
    vtk.write(save_name, file_format="vtk", binary=False)

    end_time = datetime.now()

    elasped_seconds = (end_time-start_time).total_seconds()
    print(f"Elapsed Time: {elasped_seconds}[s]")
