from iges2vtk.iges.readers.iges_reader import IgesReader

filename = "cases/iges/PN_ICP System.igs"

reader = IgesReader()

iges = reader.read_file(filename)
