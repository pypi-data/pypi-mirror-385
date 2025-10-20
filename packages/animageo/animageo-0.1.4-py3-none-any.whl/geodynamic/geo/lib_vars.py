import numpy as np

from .lib_elements import Angle

#--------------------------------------------------------------------------

class Var:
    def __init__(self, name, data = None):
        self.name = name
        self.data = data
        self.style = {}

    def __repr__(self):
        return f"{self.name}:\t{self.data}"

#--------------------------------------------------------------------------

class Measure:
    def __init__(self, x, dim = 0):
        self.x = x
        self.dim = dim
    def __repr__(self):
        return "Measure{}({})".format(self.dim, self.x)

    def translate(self, vec):
        pass
    def scale(self, ratio):
        if self.dim != 0: self.x *= ratio ** self.dim

    def equivalent(self, other):
        if not isinstance(other, Measure): return False
        return np.isclose(self.x, other.x)

class AngleSize:
    def __init__(self, x):
        self.value = x
    def __repr__(self):
        return "AngleSize({}°)".format(self.value * 180 / np.pi)

    def translate(self, vec):
        pass
    def scale(self, ratio):
        pass

    def equivalent(self, other):
        if isinstance(other, Angle): return np.isclose(self.value, other.angle)
        if isinstance(other, AngleSize): return np.isclose(self.value, other.value)
        return False

def AngleSizeFromDegrees(text):
    assert(text[-1] == '°')
    return AngleSize(float(text[:-1]) * np.pi / 180)

class Boolean:
    def __init__(self, b):
        self.b = b
    def __repr__(self):
        return "Boolean({})".format(self.b)

    def translate(self, vec):
        pass
    def scale(self, ratio):
        pass

    def equivalent(self, other):
        if not isinstance(other, Boolean): return False
        return self.b == other.b
