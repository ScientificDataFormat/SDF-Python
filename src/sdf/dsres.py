from os import PathLike

import numpy as np
from sdf import Group, Dataset
import scipy.io


# extract strings from the matrix
def strMatNormal(a):
    return ["".join(s).rstrip() for s in a]


def strMatTrans(a):
    return ["".join(s).rstrip() for s in zip(*a)]


def _split_description(
    comment: str,
) -> tuple[str | None, str | None, str | None, dict[str, str]]:
    unit = None
    display_unit = None
    info = dict()

    if comment.endswith("]"):
        i = comment.rfind("[")
        unit = comment[i + 1 : -1]
        comment = comment[0:i].strip()

    if unit is not None:
        if ":#" in unit:
            segments = unit.split(":#")
            unit = segments[0]
            for segment in segments[1:]:
                key, value = segment[1:-1].split("=")
                info[key] = value

        if "|" in unit:
            unit, display_unit = unit.split("|")

    return unit, display_unit, comment, info


def load(filename: str | PathLike, objectname: str) -> Dataset | Group:
    g_root = _load_mat(filename)

    if objectname == "/":
        return g_root
    else:
        obj = g_root
        segments = objectname.split("/")
        for s in segments:
            if s:
                obj = obj[s]
        return obj


def _load_mat(filename: str) -> Group:
    mat = scipy.io.loadmat(filename, chars_as_strings=False)

    _vars = {}
    _blocks = []

    try:
        fileInfo = strMatNormal(mat["Aclass"])
    except KeyError:
        raise Exception("File structure not supported!")

    if fileInfo[1] == "1.1":
        if fileInfo[3] == "binTrans":
            # usually files from OpenModelica or Dymola auto saved,
            # all methods rely on this structure since this was the only
            # one understand by earlier versions
            names = strMatTrans(mat["name"])  # names
            descr = strMatTrans(mat["description"])  # descriptions

            cons = mat["data_1"]
            traj = mat["data_2"]

            d = mat["dataInfo"][0, :]
            x = mat["dataInfo"][1, :]

        elif fileInfo[3] == "binNormal":
            # usually files from dymola, save as...,
            # variables are mapped to the structure above ('binTrans')
            names = strMatNormal(mat["name"])  # names
            descr = strMatNormal(mat["description"])  # descriptions

            cons = mat["data_1"].T
            traj = mat["data_2"].T

            d = mat["dataInfo"][:, 0]
            x = mat["dataInfo"][:, 1]
        else:
            raise Exception("File structure not supported!")

        c = np.abs(x) - 1  # column
        s = np.sign(x)  # sign

        vars = zip(names, descr, d, c, s)
    elif fileInfo[1] == "1.0":
        # files generated with dymola, save as..., only plotted ...
        # fake the structure of a 1.1 transposed file
        names = strMatNormal(mat["names"])  # names
        _blocks.append(0)
        mat["data_0"] = mat["data"].transpose()
        del mat["data"]
        _absc = (names[0], "")
        for i in range(1, len(names)):
            _vars[names[i]] = ("", 0, i, 1)
    else:
        raise Exception("File structure not supported!")

    # build the SDF tree
    g_root = Group("/")

    ds_time = None

    for name, desc, d, c, s in vars:
        unit, display_unit, comment, info = _split_description(desc)

        path = name.split(".")

        g_parent = g_root

        for segment in path[:-1]:
            if segment in g_parent:
                g_parent = g_parent[segment]
            else:
                g_child = Group(segment)
                g_parent.groups.append(g_child)
                g_parent = g_child
            pass

        if d == 1:
            data = cons[c, 0] * s
        else:
            data = traj[c, :] * s

        if "type" in info:
            if info["type"] == "Integer" or "Boolean":
                data = np.asarray(data, dtype=np.int32)

        if d == 0:
            ds = Dataset(
                path[-1],
                comment="Simulation time",
                unit=unit,
                display_unit=display_unit,
                data=data,
            )
            ds_time = ds
        elif d == 1:
            ds = Dataset(
                path[-1],
                comment=comment,
                unit=unit,
                display_unit=display_unit,
                data=data,
            )
        else:
            ds = Dataset(
                path[-1],
                comment=comment,
                unit=unit,
                display_unit=display_unit,
                data=data,
                scales=[ds_time],
            )

        g_parent.datasets.append(ds)

    return g_root
