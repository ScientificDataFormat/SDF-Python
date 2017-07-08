# Copyright (c) 2017 Dassault Systemes. All rights reserved.

import numpy as np
from sdf import Group, Dataset

def _split_description(comment):

    unit = None
    display_unit = None
    info = dict()

    if comment.endswith(']'):
        i = comment.rfind('[')
        unit = comment[i + 1:-1]
        comment = comment[0:i].strip()

    if unit is not None:

        if ':#' in unit:
            segments = unit.split(':#')
            unit = segments[0]
            for segment in segments[1:]:
                key, value = segment[1:-1].split('=')
                info[key] = value

        if '|' in unit:
            unit, display_unit = unit.split('|')

    return unit, display_unit, comment, info


def load(filename, objectname, unit=None, scale_units=None):

    if objectname == '/':
        return load_all(filename)
    else:
        return load_dataset(filename, objectname, unit, scale_units)


def load_dataset(filename, path, unit=None, scale_units=None):

    import DyMat

    df = DyMat.DyMatFile(filename)

    # remove the leading slash
    if path.startswith('/'):
        path = path[1:]

    # change to the path dot notation
    path = path.replace('/', '.')

    # get the variable name
    name = path.split('.')[-1]

    unit, display_unit, comment, info = _split_description(df.description(path))

    data = df.data(path)

    if 'type' in info:
        if info['type'] == 'Integer' or 'Boolean':
            data = np.asarray(data, dtype=np.int32)

    if data.size == 2:
        ds = Dataset(name, comment=comment, unit=unit, display_unit=display_unit, data=data[0])
    else:
        a_data, a_name, a_description = df.abscissa(2)
        a_unit, _, a_comment, a_info = _split_description(a_description)

        ds_time = Dataset(a_name, data=a_data, unit=a_unit, comment='Simulation time')

        ds = Dataset(name, comment=comment, unit=unit, display_unit=display_unit, data=data, scales=[ds_time])

    return ds


def load_all(filename):

    import DyMat

    g_root = Group('/')

    df = DyMat.DyMatFile(filename)

    data, name, description = df.abscissa(2)
    unit, display_unit, comment, info = _split_description(description)

    ds_time = Dataset(name, data=data, unit=unit, comment='Simulation time')
    g_root.datasets.append(ds_time)

    for name in df.names():

        unit, display_unit, comment, info = _split_description(df.description(name))

        path = name.split('.')

        g_parent = g_root

        for segment in path[:-1]:
            if segment in g_parent:
                g_parent = g_parent[segment]
            else:
                g_child = Group(segment)
                g_parent.groups.append(g_child)
                g_parent = g_child
            pass

        data = df.data(name)

        if 'type' in info:
            if info['type'] == 'Integer' or 'Boolean':
                data = np.asarray(data, dtype=np.int32)

        if data.size == 2:
            ds = Dataset(path[-1], comment=comment, unit=unit, display_unit=display_unit, data=data[0])
        else:
            ds = Dataset(path[-1], comment=comment, unit=unit, display_unit=display_unit, data=data, scales=[ds_time])

        g_parent.datasets.append(ds)

    return g_root
