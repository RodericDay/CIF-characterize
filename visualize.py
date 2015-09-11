import numpy as np
from scipy import ndimage, spatial

import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


fig = plt.figure()
projection = False
ax = fig.add_subplot(221 if projection else 111, projection='3d')

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

if __name__ == '__main__':
    from characterize import load_pdb
    from bresenham import bresenhamline

    points, conns = map(np.array, load_pdb('CHA'))
    points -= points.min(axis=0)

    marked = []
    for a, b in points[conns]*4:

        # original
        x, y, z = np.transpose([a, b])
        ax.plot(x, y, z, 'r')

        # rasterized?
        x, y, z = np.transpose(bresenhamline(np.atleast_2d(a), b, -1))
        ax.plot(x, y, z, 'b')
        marked.extend( map(tuple, np.transpose([x, y, z]).astype(int).tolist()) )

    marked_a = np.array(marked)
    size = marked_a.max(axis=0) - marked_a.min(axis=0) + 1
    canvas = np.ones(size, dtype=bool)
    offset = marked_a.min(axis=0)

    for idx, _ in np.ndenumerate(canvas):
        if idx in marked:
            canvas[idx] = 0

    if projection:
        for d in range(3):
            fig.add_subplot(222+d).matshow(canvas.sum(axis=d))

    centers, radii = extract_spheres(canvas)
    print(len(centers), "spheres found")

    # plot the nodes of these "spheres"
    x, y, z = np.transpose(centers + offset)
    ax.scatter(x, y, z, 'g', s=radii*200)

    # tesselate to see how they connect
    for a, b in (centers + offset)[spatial.Voronoi(centers).ridge_points]:
        x, y, z = np.transpose([a, b])
        ax.plot(x, y, z, 'g')

plt.show()
