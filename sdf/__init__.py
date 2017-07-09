# Copyright (c) 2017 Dassault Systemes. All rights reserved.

import numpy as np
from .units import convert_unit
import re
from copy import copy

from . import hdf5

__version__ = '0.3.2'

_object_name_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_]*')


class Group(object):
    """ SDF Group """

    def __init__(self, name, comment=None, attributes=dict(), groups=[], datasets=[]):
        self.name = name
        self.comment = comment
        self.attributes = copy(attributes)
        self.groups = copy(groups)
        self.datasets = copy(datasets)

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

    def __repr__(self):
        return '<SDF Group "' + self.name + '": [' + ', '.join(map(lambda obj: obj.name, self)) + ']>'


class Dataset(object):
    """ SDF Dataset """

    def __init__(self, name,
                 comment=None,
                 attributes=dict(),
                 data=np.empty(0),
                 display_name=None,
                 relative_quantity=False,
                 unit=None,
                 display_unit=None,
                 is_scale=False,
                 scales=[]
                 ):
        self.name = name
        self.comment = comment
        self.attributes = copy(attributes)
        self.data = data
        self._display_name = display_name
        self.relative_quantity = relative_quantity
        self.unit = unit
        self._display_unit = display_unit
        self.is_scale = is_scale
        self.scales = scales

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

    def validate(self):
        if self.display_unit and not self.unit:
            return 'ERROR', 'display_unit was set but no unit'

        return 'OK'

    # some shorthand aliases
    @property
    def d(self):
        return self.data

    dd = display_data

    def __repr__(self):
        text = '<SDF Dataset "' + self.name + '": '

        if not isinstance(self.data, np.ndarray) or len(self.data.shape) == 0:
            text += str(self.data)
        elif len(self.data.shape) == 1 and len(self.data) <= 10:
            text += str(self.data)
        else:
            text += '<' + 'x'.join(map(str, self.data.shape)) + '>'

        if self.unit is not None:
            text += ' ' + self.unit

        if any(self.scales):
            text += ' w.r.t. ' + ', '.join(map(lambda s: s.name if s is not None else 'None', self.scales))

        text += '>'

        return text


def validate(obj):
    """ Validate an sdf.Group or sdf.Dataset """

    errors = []

    if isinstance(obj, Group):
        errors += _validate_group(obj, is_root=True)
    elif isinstance(obj, Dataset):
        errors += _validate_dataset(obj)
    else:
        errors.append('Unknown object type: %s' % type(obj))

    return errors


def _validate_group(group, is_root=False):
    errors = []

    if not is_root and not _object_name_pattern.match(group.name):
        errors += [
            "Object names must only contain letters, digits and underscores (\"_\") and must start with a letter"]

    for child_group in group.groups:
        errors += _validate_dataset(child_group)

    for ds in group.datasets:
        errors += _validate_dataset(ds)

    return errors


def _validate_dataset(ds):
    if not type(ds.data) is np.ndarray:
        return ['Dataset.data must be a numpy.ndarray']

    elif np.alen(ds.data) < 1:
        return ['Dataset.data must not be empty']

    elif not np.issubdtype(ds.data.dtype, np.float64):
        return ['Dataset.data.dtype must be numpy.float64']

    if ds.is_scale:
        if len(ds.data.shape) != 1:
            return ['Scales must be one-dimensional']
        if np.any(np.diff(ds.data) <= 0):
            return ['Scales must be strictly monotonic increasing']
    else:
        if (len(ds.data.shape) >= 1) and (ds.data.shape[0] > 0) and not (len(ds.data.shape) == len(ds.scales)):
            return ['The number of scales does not match the number of dimensions']

    return []


def load(filename, objectname='/', unit=None, scale_units=None):
    """ Load a dataset or group from an SDF file """

    obj = None

    if filename.endswith('.mat'):
        from . import dsres
        obj = dsres.load(filename, objectname)
    else:
        obj = hdf5.load(filename, objectname)

    if isinstance(obj, Dataset):

        # check the unit
        if unit is not None and unit != obj.unit:
            raise Exception("Dataset '%s' has the wrong unit. Expected '%s' but was '%s'." % (obj.name, unit, obj.unit))

        # check the number of the scale units
        if scale_units is not None:

            if len(scale_units) != obj.data.ndim:
                raise Exception("The number of scale units must be equal to the number of dimensions. " +
                                "Dataset '%s' has %d dimension(s) but %d scale units where given."
                                % (obj.name, obj.data.ndim, len(scale_units)))

            # check the scale units
            for i, scale_unit in enumerate(scale_units):
                scale = obj.scales[i]
                if scale.unit != scale_unit:
                    raise Exception(("The scale for dimension %d of '%s' has the wrong unit. " +
                                    "Expected '%s' but was '%s'.") % (i + 1, obj.name, scale_unit, scale.unit))

    return obj


def save(filename, group):
    """ Save an SDF group to a file """

    hdf5.save(filename, group)
