import math
from Geometry import Point


__author__ = 'Tan'


def get_vector_length(vector):
    return math.sqrt(vector.x * vector.x + vector.y * vector.y)


def get_angle_between_two_vectors(a, b):
    len_a = get_vector_length(a)
    len_b = get_vector_length(b)

    if len_a * len_b == 0:
        return 0

    c = (a.x * b.x + a.y * b.y) / (len_a * len_b)
    if c >= 1:
        return 0
    return math.acos(c)


def calculate_tri_area(point1, point2, point3):
    vector1 = Point.Point(point1.x - point2.x, point1.y - point2.y)
    vector2 = Point.Point(point3.x - point2.x, point3.y - point2.y)

    len1 = get_vector_length(vector1)
    len2 = get_vector_length(vector2)

    dot_product = vector1.x * vector2.x + vector1.y * vector2.y
    t = 0 if len1 == 0 or len2 == 0 else dot_product / len1 / len2
    t = 1 if t > 1 else t
    t = -1 if t < -1 else t
    angle = math.acos(t)

    return len1 * math.sin(angle) * len2 / 2
