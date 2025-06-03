from __future__ import annotations
from os import PathLike
import numpy as np
from .units import convert_unit
import re
from attrs import define, field

from . import hdf5

__version__ = "0.3.7"

_object_name_pattern = re.compile("[a-zA-Z][a-zA-Z0-9_]*")


@define(eq=False)
class Group:
    """SDF Group"""

    name: str = None
    comment: str = None
    attributes: dict[str, str] = field(factory=dict)
    groups: list[Group] = field(factory=list)
    datasets: list[Dataset] = field(factory=list)

    def __contains__(self, key):
        for obj in self.datasets + self.groups:
            if obj.name == key:
                return True
        return False

    def __getitem__(self, key):
        for obj in self.datasets + self.groups:
            if obj.name == key:
                return obj
        return None

    def __iter__(self):
        for obj in self.groups + self.datasets:
            yield obj


@define(eq=False)
class Dataset:
    """SDF Dataset"""

    name: str = None
    comment: str = None
    attributes: dict[str, str] = field(factory=dict)
    data: np.typing.NDArray = None
    _display_name: str = None
    relative_quantity: bool = False
    unit: str = None
    _display_unit: str = None
    is_scale: bool = False
    scales: list[Dataset] = field(factory=list)

    @property
    def display_data(self):
        return convert_unit(self.data, self.unit, self.display_unit)

    @display_data.setter
    def display_data(self, value):
        self.data = convert_unit(value, self.display_unit, self.unit)

    @property
    def display_name(self):
        return self._display_name if self._display_name else self.name

    @display_name.setter
    def display_name(self, value):
        self._display_name = value

    @property
    def display_unit(self):
        return self._display_unit if self._display_unit else self.unit

    @display_unit.setter
    def display_unit(self, value):
        self._display_unit = value

    # some shorthand aliases
    @property
    def d(self):
        return self.data

    dd = display_data


def validate(obj: Group | Dataset) -> list[str]:
    """Validate an sdf.Group or sdf.Dataset"""

    problems = []

    if isinstance(obj, Group):
        problems += _validate_group(obj, is_root=True)
    elif isinstance(obj, Dataset):
        problems += _validate_dataset(obj)
    else:
        problems.append(f"Unknown object type: {type(obj)}")

    return problems


def _validate_group(group, is_root=False):
    problems = []

    if not is_root and not _object_name_pattern.match(group.name):
        problems.append(
            'Object names must only contain letters, digits, and underscores ("_") and must start with a letter.'
        )

    for child_group in group.groups:
        problems += _validate_dataset(child_group)

    for ds in group.datasets:
        problems += _validate_dataset(ds)

    return problems


def _validate_dataset(ds: Dataset) -> list[str]:
    if type(ds.data) is not np.ndarray:
        return ["Dataset.data must be a numpy.ndarray"]

    elif ds.data.size < 1:
        return ["Dataset.data must not be empty"]

    elif not np.issubdtype(ds.data.dtype, np.float64):
        return ["Dataset.data.dtype must be numpy.float64"]

    if ds.is_scale:
        if len(ds.data.shape) != 1:
            return ["Scales must be one-dimensional"]
        if np.any(np.diff(ds.data) <= 0):
            return ["Scales must be strictly monotonic increasing"]
    else:
        if (
            (len(ds.data.shape) >= 1)
            and (ds.data.shape[0] > 0)
            and not (len(ds.data.shape) == len(ds.scales))
        ):
            return ["The number of scales does not match the number of dimensions"]

    return []


def load(
    filename: str | PathLike,
    objectname: str = "/",
    unit: str = None,
    scale_units: list[str] = None,
) -> Dataset | Group:
    """Load a Dataset or Group from an SDF file"""

    if filename.endswith(".mat"):
        from . import dsres

        obj = dsres.load(filename, objectname)
    else:
        obj = hdf5.load(filename, objectname)

    if isinstance(obj, Dataset):
        # check the unit
        if unit is not None and unit != obj.unit:
            raise Exception(
                "Dataset '%s' has the wrong unit. Expected '%s' but was '%s'."
                % (obj.name, unit, obj.unit)
            )

        # check the number of the scale units
        if scale_units is not None:
            if len(scale_units) != obj.data.ndim:
                raise Exception(
                    "The number of scale units must be equal to the number of dimensions. "
                    + "Dataset '%s' has %d dimension(s) but %d scale units where given."
                    % (obj.name, obj.data.ndim, len(scale_units))
                )

            # check the scale units
            for i, scale_unit in enumerate(scale_units):
                scale = obj.scales[i]
                if scale.unit != scale_unit:
                    raise Exception(
                        (
                            "The scale for dimension %d of '%s' has the wrong unit. "
                            + "Expected '%s' but was '%s'."
                        )
                        % (i + 1, obj.name, scale_unit, scale.unit)
                    )

    return obj


def save(filename: str | PathLike, group: Group):
    """Save an SDF group to a file"""

    hdf5.save(filename, group)
