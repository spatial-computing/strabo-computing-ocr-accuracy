from Geometry import Point
import numpy as np


__author__ = 'Tan'


class Line:
    def __init__(self, point1, point2):
        self.start_point = point1
        self.direction = Point.Point(point2.x - point1.x, point2.y - point1.y)

    def find_intersection_point(self, line2):
        # Calculate the intersection point.
        A = np.array([ [self.direction.x, -1 * line2.direction.x],
                    [self.direction.y, -1 * line2.direction.y] ])
        y = np.array([ [line2.start_point.x - self.start_point.x],
                    [line2.start_point.y - self.start_point.y] ])

        # If the two lines are parallel, then A is not invertible.
        det = np.linalg.det(A)
        if det == 0:
            return Point.Point(-1, -1)

        ans = np.linalg.solve(A, y)

        t0 = ans[0][0]
        t1 = ans[1][0]

        if t0 < 0 or t1 < 0 or t0 > 1 or t1 > 1:
            return Point.Point(-1, -1)
        else:
            return Point.Point(self.start_point.x + t0 * self.direction.x, self.start_point.y + t0 * self.direction.y)

if __name__ == '__main__':
    p1 = Point.Point(0, 0)
    p2 = Point.Point(2, 2)
    p3 = Point.Point(0, 2)
    p4 = Point.Point(2, 0)

    l1 = Line(p1, p2)
    l2 = Line(p3, p2)

    ans = l1.find_intersection_point(l2)
    print('x: %f, y: %f.' % (ans.x, ans.y))
