import re
import numpy as np
from scipy import ndimage, spatial

import bresenham

import mpl_tools
import vtk_tools


def load_pdb(name):
    with open(name+'.pdb') as fp:
        points = []
        conns = []

        for line in fp:

            if line.startswith('HET'):
                pattern = r'(-?\d+.\d\d\d)'
                x, y, z = (float(c) for c in re.findall(pattern, line))
                points.append([x, y, z])

            elif line.startswith('CON'):
                pattern = r'(\d+)'
                ids = (int(c) for c in re.findall(pattern, line))
                first = next(ids)
                conns.extend([(first-1, other-1) for other in ids])

    return points, conns

def extract_spheres(im):
    '''
    credit to untubu @ stackoverflow for this
    still needs a lot of improvement
    '''
    im = np.atleast_3d(im)
    data = ndimage.morphology.distance_transform_edt(im)
    max_data = ndimage.filters.maximum_filter(data, 10)
    maxima = data==max_data # but this includes some globally low voids
    min_data = ndimage.filters.minimum_filter(data, 10)
    diff = (max_data - min_data) > 1
    maxima[diff==0] = 0

    labels, num_maxima = ndimage.label(maxima)
    centers = [ndimage.center_of_mass(labels==i) for i in range(1, num_maxima+1)]
    radii = [data[center] for center in centers]
    return np.array(centers), np.array(radii)

def rasterize():
    pass

solid_nodes, solid_edges = map(np.array, load_pdb('CHA'))
solid_nodes -= solid_nodes.min(axis=0)
solid_nodes *= 4

coord_pair = solid_nodes[solid_edges]

discretized = []
for a, b in coord_pair:
    point_list = bresenham.bresenhamline(np.atleast_2d(a), b, -1).astype(int).tolist()
    discretized.extend([tuple(point) for point in point_list])

array = np.array(discretized)
size = array.max(axis=0) - array.min(axis=0) + 1
canvas = np.ones(size, dtype=bool)
offset = array.min(axis=0)

for idx, _ in np.ndenumerate(canvas):
    if idx in discretized:
        canvas[idx] = 0

# mpl_tools.visualize(canvas)

centers, radii = extract_spheres(canvas)

vtk_tools.visualize(solid_nodes, solid_edges, centers, radii)