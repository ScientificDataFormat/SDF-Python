from __future__ import annotations
import h5py
import sdf
import numpy as np
import os
import sys


def _to_python_str(s):
    """Convert to Python string"""

    if isinstance(s, bytes):
        return s.decode("utf-8")
    else:
        return s


def load(filename: str | os.PathLike, objectname: str) -> sdf.Dataset | sdf.Group:
    with h5py.File(filename, "r") as f:
        datasets = {}

        dsobj = f[objectname]
        class_name = dsobj.__class__.__name__

        if class_name == "Group":
            group = _create_group(dsobj, datasets)
            _restore_scales(datasets)
            return group
        elif class_name == "Dataset":
            dataset = _create_dataset(dsobj, datasets)

            for ri in range(dsobj.ndim):
                if dsobj.dims[ri]:
                    sobj = dsobj.dims[ri][0]
                    s = _create_dataset(sobj, dict())
                    s.is_scale = True
                    dataset.scales[ri] = s

            return dataset

        else:
            raise Exception("Unexpected object")


def save(filename: str | os.PathLike, group: sdf.Group) -> None:
    with h5py.File(filename, "w") as f:
        datasets = dict()
        _write_group(f, group, "/", datasets)

        # attach the scales
        for ds, h5ds in datasets.items():
            for i, s in enumerate(ds.scales):
                if s is None:
                    continue
                elif s in datasets:
                    h5s = datasets[s]
                    dimname = s._display_name
                    if dimname is None:
                        dimname = ""
                    h5s.make_scale(_str(dimname))
                    h5ds.dims[i].attach_scale(h5s)
                else:
                    print(
                        "Cannot attach scale for '"
                        + h5ds.name
                        + "' because the referenced scale for dimension "
                        + str(i)
                        + " is not part of the file"
                    )


def _create_group(gobj, datasets):
    """Create an sdf.Group from an h5py group"""

    ds_obj_list = []
    g_obj_list = []

    group_attrs = {
        key: gobj.attrs[key] for key in gobj.attrs.keys() if key != "COMMENT"
    }
    comment = gobj.attrs.get("COMMENT")

    for ds_name in gobj.keys():
        # TODO: fix this?
        if isinstance(gobj[ds_name], h5py._hl.dataset.Dataset):
            ds_obj_list.append(gobj[ds_name])
        elif isinstance(gobj[ds_name], h5py._hl.group.Group):
            g_obj_list.append(gobj[ds_name])

    child_groups = []

    for cgobj in g_obj_list:
        child_groups.append(_create_group(cgobj, datasets))

    ds_list = [_create_dataset(dsobj, datasets) for dsobj in ds_obj_list]

    name = gobj.name.split("/")[-1]

    return sdf.Group(
        name=name,
        comment=comment,
        attributes=group_attrs,
        groups=child_groups,
        datasets=ds_list,
    )


def _create_dataset(dsobj, datasets):
    """Create a dataset from an h5py dataset"""

    _, name = os.path.split(dsobj.name)
    ds = sdf.Dataset(name, data=dsobj[()])

    for attr in dsobj.attrs:
        if attr == "COMMENT":
            ds.comment = _to_python_str(dsobj.attrs[attr])
        elif attr == "NAME":
            ds.display_name = _to_python_str(dsobj.attrs[attr])
        elif (
            attr == "RELATIVE_QUANTITY" and _to_python_str(dsobj.attrs[attr]) == "TRUE"
        ):
            ds.relative_quantity = True
        elif attr == "UNIT":
            ds.unit = _to_python_str(dsobj.attrs[attr])
        elif attr == "DISPLAY_UNIT":
            ds.display_unit = _to_python_str(dsobj.attrs[attr])
        elif attr == "CLASS" and _to_python_str(dsobj.attrs[attr]) == "DIMENSION_SCALE":
            ds.is_scale = True
        elif attr == "REFERENCE_LIST":
            ds.is_scale = True
        elif attr in ["REFERENCE_LIST", "DIMENSION_LIST"]:
            pass
        else:
            ds.attributes[attr] = _to_python_str(dsobj.attrs[attr])

    ds.scales = [None] * ds.data.ndim

    datasets[dsobj] = ds

    return ds


def _restore_scales(datasets):
    for dsobj, ds in datasets.items():
        for i in range(ds.data.ndim):
            if dsobj.dims[i]:
                sobj = dsobj.dims[i][0]
                scale = datasets[sobj]
                scale.is_scale = True
                ds.scales[i] = scale
                pass


def _str(s):
    """Convert to byte string"""

    if sys.version_info.major >= 3 and isinstance(s, bytes):
        return s
    else:
        # convert the string to an fixed-length utf-8 byte string
        return np.bytes_(s.encode("utf-8"))


def _write_group(f, g, path, datasets):
    if path == "/":
        gobj = f
    else:
        gobj = f.create_group(path)

    # iterate over the child groups
    for subgroup in g.groups:
        _write_group(f, subgroup, path + subgroup.name + "/", datasets)

    if g.comment is not None:
        gobj.attrs["COMMENT"] = _str(g.comment)

    for key, value in g.attributes.items():
        gobj.attrs[key] = _str(value)

    # write the datasets
    for ds in g.datasets:
        _write_dataset(f, ds, path, datasets)


def _write_dataset(f, ds, path, datasets):
    f[path + ds.name] = ds.data
    dsobj = f[path + ds.name]

    datasets[ds] = dsobj

    if ds.comment:
        dsobj.attrs["COMMENT"] = _str(ds.comment)

    if ds._display_name:
        dsobj.attrs["NAME"] = _str(ds.display_name)

    if ds.relative_quantity:
        dsobj.attrs["RELATIVE_QUANTITY"] = _str("TRUE")

    if ds.unit:
        dsobj.attrs["UNIT"] = _str(ds.unit)

    if ds.display_unit != ds.unit:
        dsobj.attrs["DISPLAY_UNIT"] = _str(ds.display_unit)

    if ds.is_scale:
        dimname = ds.display_name

        if dimname is None:
            dimname = ""

        h5py.h5ds.set_scale(dsobj.id, _str(dimname))

    return dsobj
