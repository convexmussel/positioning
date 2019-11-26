import numpy as np
import pandas as pd
import math
class Point3D:
    def __init__(self, location, value=None):
        self.location = location
        self.point_value = None

    def __add__(self, other):
        if type(other) is Point3D:
            return self.location + other.location
        else:
            return self.location + other

    def __sub__(self, other):
        if type(other) is Point3D:
            return self.location - other.location
        else:
            return self.location - other

    def __mul__(self, other):
        if type(other) is Point3D:
            return self.location * other.location
        else:
            print(self.location)
            return self.location * other

    def __gt__(self, other):
        if self.point_value > other.point_value:
            return True
        return False

    def __le__(self, other):
        if self.point_value <= other.point_value:
            return True
        return False

    def __ge__(self, other):
        if self.point_value >= other.point_value:
            return True
        return False

    def __lt__(self, other):
        if self.point_value < other.point_value:
            return True
        return False

    def __len__(self):
        return len(self.location)

    def __getitem__(self, key):
        return self.location[key]

    def __setitem__(self, key, value):
        self.location[key] = value
        return True
