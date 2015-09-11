import re

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

