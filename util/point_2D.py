class Point2D:

    def __init__(self, location, value=None):
        self.x_location, self.y_location = location
        self.point_value = value

    def set_location(self, location):
        self.x_location, self.y_location = location

    def get_x_location(self):
        return self.x_location

    def get_y_location(self):
        return self.y_location

    def get_location(self):
        return self.x_location, self.y_location

    def print_location(self):
        print([self.x_location, self.y_location])

    def set_value(self, value):
        self.point_value = value

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

    def __ne__(self, other):
        if self.point_value != other.point_value:
            return True
        return False

    def __lt__(self, other):
        if self.point_value < other.point_value:
            return True
        return False

    def __eq__(self, other):
        if self.point_value == other.point_value:
            return True
        return False
