from pygmsh import geo
import gmsh

gmsh.initialize()
gmsh.merge("cases/igs/PN_ICP System.igs")
gmsh.option.setNumber("Mesh.Algorithm", 8)

gmsh.model.mesh.generate(3)
gmsh.write("PN_ICP System.vtk")


gmsh.finalize()
