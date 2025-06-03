import math


class Table(object):
    """
    Utility class to store the unit conversions (inspired by Guava's com.google.common.collect.Table<R,C,V>)
    """

    def __init__(self):
        self._rows = dict()

    def put(self, row_key, column_key, value):
        if row_key in self._rows:
            self._rows[row_key][column_key] = value
        else:
            self._rows[row_key] = {column_key: value}

    def get(self, row_key, column_key):
        if row_key in self._rows:
            return self._rows[row_key][column_key]
        else:
            return None


global _converters
_converters = Table()


def convert_unit(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value  # nothing to do

    converter = _converters.get(from_unit, to_unit)

    if not converter:
        raise Exception(
            'No conversion defined for "' + from_unit + '" -> "' + to_unit + '"'
        )

    return converter.convert(value)


class LinearUnitConverter(object):
    def __init__(self, from_unit, to_unit, factor, offset=0):
        self.from_unit = from_unit
        self.to_unit = to_unit
        self.factor = factor
        self.offset = offset

    def convert(self, value):
        return value * self.factor + self.offset


def define_unit_conversion(from_unit, to_unit, factor, offset=0):
    global _converters
    _converters.put(
        from_unit, to_unit, LinearUnitConverter(from_unit, to_unit, factor, offset)
    )
    _converters.put(
        to_unit,
        from_unit,
        LinearUnitConverter(to_unit, from_unit, 1 / factor, -offset / factor),
    )


# Time
define_unit_conversion("s", "ms", 1000)
define_unit_conversion("s", "min", 1.0 / 60.0)
define_unit_conversion("s", "h", 1.0 / 3600.0)
define_unit_conversion("s", "d", 1.0 / 86400.0)

# Angle
define_unit_conversion("rad", "deg", 180 / math.pi)

# Angular velocity
define_unit_conversion("rad/s", "deg/s", 180 / math.pi)
define_unit_conversion("rad/s", "rpm", 30 / math.pi)
define_unit_conversion("rad/s", "1/min", 30 / math.pi)
define_unit_conversion("rad/s", "r/min", 30 / math.pi)

# Length, distance
define_unit_conversion("m", "km", 0.001)
# define_unit_conversion('m', 'cm', 100)
define_unit_conversion("m", "mm", 1000)

# Area
# define_unit_conversion('m2','cm2',1e4)

# Volume
define_unit_conversion("m3", "l", 1e3)
define_unit_conversion("m3", "ml", 1e6)

# Pressure
define_unit_conversion("Pa", "kPa", 1e-3)
define_unit_conversion("Pa", "MPa", 1e-6)
define_unit_conversion("Pa", "bar", 1e-5)

# Bulk Modulus
define_unit_conversion("N/m2", "bar", 1 / 1e5)

# Volume Flow Rate
define_unit_conversion("m3/s", "l/min", 1e3 * 60)

# Density
define_unit_conversion("kg/m3", "kg/dm3", 1e-3)
define_unit_conversion("kg/m3", "kg/l", 1e-3)
# define_unit_conversion('kg/m3', 'g/cm3', 1e-3)
# define_unit_conversion('kg/s', 'g/s', 1e3)

# Speed
define_unit_conversion("m/s", "km/h", 3.6)
define_unit_conversion("m/s", "mm/s", 1e3)
# define_unit_conversion('m/s', 'knots', 1.9438445)

# Force
define_unit_conversion("N", "mN", 1000)
define_unit_conversion("N", "kN", 1e-3)
define_unit_conversion("N", "MN", 1e-6)

# Work, Energy
define_unit_conversion("J", "kWh", 1.0 / 3600.0 / 1000.0)
define_unit_conversion("J", "mJ", 1000)
define_unit_conversion("J", "kJ", 1e-3)
define_unit_conversion("J", "MJ", 1e-6)

# Power
define_unit_conversion("W", "mW", 1000)
define_unit_conversion("W", "kW", 1e-3)
define_unit_conversion("W", "MW", 1e-6)

# Temperature
define_unit_conversion("K", "degC", 1, -273.15)

# Voltage
define_unit_conversion("V", "mV", 1000)
define_unit_conversion("V", "kV", 0.001)

# Currrent
define_unit_conversion("A", "mA", 1000)
define_unit_conversion("A", "kA", 0.001)

# Capacitance
define_unit_conversion("F", "uF", 1e6)

# Leakage
define_unit_conversion("m3/(s.Pa)", "l/(min.bar)", 6e9)

# Viscous Friction
# define_unit_conversion('N.m/(rad/s)', 'N.m/(rev/min)',0.10471975512)

# Kinematic Viscosity
define_unit_conversion("m2/s", "mm2/s", 1e6)

# Temperature coefficient (e.g. of resistance)
define_unit_conversion("1/K", "ppm/K", 1e6)
