from Geometry import Line, Point
from Geometry import GeoOperations
import math, sys

__author__ = 'Tan'


class Polygon:
    def __init__(self, points):
        self.points = []
        self.lines = []

        x = y = 0
        for point in points:
            self.points.append(point)
            x += point.x
            y += point.y

            if len(self.points) > 1:
                self.lines.append(Line.Line(self.points[-2], self.points[-1]))

        self.lines.append(Line.Line(self.points[-1], self.points[0]))
        self.center = Point.Point(float(x)/len(points), float(y)/len(points))

    def __str__(self):
        string = ''
        for point in self.points:
            string = string + point.__str__() + "\n"
        return string

    def get_point_list(self):
        point_list = []
        for point in self.points:
            temp = [point.x, point.y]
            point_list.append(temp)
        return [point_list]

    def get_area(self):
        point_num = len(self.points)
        point1 = self.points[0]
        area_sum = 0
        for i in range(2, point_num, 1):
            point2 = self.points[i - 1]
            point3 = self.points[i]

            area_sum += GeoOperations.calculate_tri_area(point1, point2, point3)
        return area_sum

    def scale(self, factor_w, factor_h):
        for point in self.points:
            point.x *= factor_w
            point.y *= factor_h

        self.lines = []

        for i in range(0, 3):
            self.lines.append(Line.Line(self.points[i], self.points[i+1]))

        self.lines.append(Line.Line(self.points[-1], self.points[0]))

    def get_xywh(self):
        xs = []
        ys = []

        for point in self.points:
            xs.append(math.fabs(point.x))
            ys.append(math.fabs(point.y))

            x = min(xs)
            y = min(ys)
            w = max(xs) - x
            h = max(ys) - y

        return (x, y, w, h)

    def get_polygon_distance(self, poly2):
        # dist = sys.maxsize
        # [x1, y1, w1, h1] = self.get_xywh()
        # [x2, y2, w2, h2] = poly2.get_xywh()
        #
        # dist = math.fabs(x1 - x2)
        # dist = min(dist, math.fabs(x1 + w1 - x2))
        # dist = min(dist, math.fabs(x1 - x2 - w2))
        # dist = min(dist, math.fabs(x1 + w1 - x2 - w2))
        #
        # dist = min(dist, math.fabs(y1 - y2))
        # dist = min(dist, math.fabs(y1 + h1 - y2))
        # dist = min(dist, math.fabs(y1 - y2 - h2))
        # dist = min(dist, math.fabs(y1 + h1 - y2 - h2))
        dist = self.center.get_point_dist(poly2.center)

        return dist