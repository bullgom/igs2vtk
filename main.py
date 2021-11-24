from iges2vtk.iges.readers.iges_reader import IgesReader

if __name__ == "__main__":
    filename = "cases/iges/PN_ICP System.igs"

    reader = IgesReader()

    iges = reader.read_file(filename)
