import pyvista as pv
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("filename", type=str)

if __name__ == "__main__":
    args = ap.parse_args()
    d = pv.read(args.filename)

    d.plot(show_bounds=True, point_size=1)
