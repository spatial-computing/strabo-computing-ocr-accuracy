__author__ = 'Tan'


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (other.x == self.x) and (other.y == self.y)

    def __ne__(self, other):
        return (other.x != self.x) or (other.y != self.y)

    def __str__(self):
        return '[%f, %f],' % (self.x, self.y)
