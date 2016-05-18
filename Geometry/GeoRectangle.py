from Geometry import Point
from Geometry import Line
from Geometry import Polygon
from Geometry import GeoOperations
import math

__author__ = 'Tan'


class GeoRectangle(Polygon.Polygon):
    def __init__(self, coordinates, text):
        points = []
        self.text = text
        self.textFound = [False] * len(text)

        for i in range(0, 4, 1):
            coordinate = coordinates[i]
            x = coordinate[0]
            y = coordinate[1]

            point = Point.Point(x, y)
            points.append(point)

        Polygon.Polygon.__init__(self, points)


    def is_the_same_rect(self, rect2):
        for point in self.points:
            found_match_point = False
            for point2 in rect2.points:
                if math.fabs(point.x - point2.x) < 2 and math.fabs(point.y - point2.y) < 3:
                    found_match_point = True

            if not found_match_point:
                return False

        return True


    def is_point_in_the_rectangle(self, point):
        for i in range(1, 5, 1):
            p0 = self.points[i % 4]
            p1 = self.points[(i + 1) % 4]
            p3 = self.points[(i + 3) % 4]

            angle1 = GeoOperations.get_angle_between_two_vectors(Point.Point(p3.x - p0.x, p3.y - p0.y),
                                                                 Point.Point(p1.x - p0.x, p1.y - p0.y))
            angle2 = GeoOperations.get_angle_between_two_vectors(Point.Point(point.x - p0.x, point.y - p0.y),
                                                                 Point.Point(p1.x - p0.x, p1.y - p0.y))
            angle3 = GeoOperations.get_angle_between_two_vectors(Point.Point(point.x - p0.x, point.y - p0.y),
                                                                 Point.Point(p3.x - p0.x, p3.y - p0.y))

            if angle2 > angle1 or angle3 > angle1:
                return False

        return True

    # Return the center of the polygon.
    def get_center(self):
        x_sum = y_sum = count = 0
        for point in self.points:
            x_sum += point.x
            y_sum += point.y
            count += 1
        return float(x_sum) / count, float(y_sum) / count

    def __reorder_intersection_points(self, old_seq, new_seq, lines):
        if len(old_seq) == 0:
            if len(new_seq) > 0:
                new_line = Line.Line(new_seq[0], new_seq[-1])
                for line in lines:
                    intersection_point = line.find_intersection_point(new_line)
                    if (intersection_point not in new_seq) and (intersection_point != Point.Point(-1, -1)):
                        return []
            return new_seq
        else:
            for i in range(0, len(old_seq), 1):
                point = old_seq[i]
                if len(new_seq) == 0:
                    new_seq.append(point)
                    old_seq.pop(i)
                    result = self.__reorder_intersection_points(old_seq, new_seq, lines)
                    if len(result) != 0:
                        return result
                    else:
                        new_seq.pop(-1)
                        old_seq.insert(i, point)
                else:
                    new_line = Line.Line(point, new_seq[-1])
                    for line in lines:
                        intersection_point = line.find_intersection_point(new_line)
                        if (intersection_point not in new_seq) and (intersection_point != Point.Point(-1, -1)):
                            return []
                    new_seq.append(point)
                    old_seq.pop(i)
                    lines.append(new_line)
                    result = self.__reorder_intersection_points(old_seq, new_seq, lines)
                    if len(result) != 0:
                        return result
                    else:
                        new_seq.pop(-1)
                        lines.pop(-1)
                        old_seq.insert(i, point)
            return []

    def get_overlap_polygon(self, polygon2):
        intersection_points = []

        # Determine whether the points in polygon2 are in the rectangle
        for point in polygon2.points:
            if self.is_point_in_the_rectangle(point):
                intersection_points.append(point)

        for point in self.points:
            if polygon2.is_point_in_the_rectangle(point) and point not in intersection_points:
                intersection_points.append(point)

        # Put the edges intersection points into the list.
        for p1_line in self.lines:
            for p2_line in polygon2.lines:
                point = p1_line.find_intersection_point(p2_line)
                if (point.x != -1 or point.y != -1) and (point not in intersection_points):
                    intersection_points.append(point)
                point = p2_line.find_intersection_point(p1_line)
                if (point.x != -1 or point.y != -1) and (point not in intersection_points):
                    intersection_points.append(point)

        # Reorder the intersection points.
        intersection_points = self.__reorder_intersection_points(intersection_points, [], [])
        if len(intersection_points) == 0:
            return None
        return Polygon.Polygon(intersection_points)


if __name__ == '__main__':
    # Test 1.
    coordinates = [
        [ 814.90350707725656, -487.75083462365137 ],
        [ 909.77324679698029, -486.51876008183683 ],
        [ 909.77324679698029, -507.46402729268493 ],
        [ 814.90350707725656, -509.3121391054068 ],
        [ 814.90350707725656, -487.75083462365137 ]
    ]

    rect = GeoRectangle(coordinates)
    rect2 = GeoRectangle(coordinates)
    polygon = rect.get_overlap_polygon(rect2)

    # Test 2.
    coordinates2 = [
        [ 0, 0 ],
        [ 2, 0 ],
        [ 2, 2 ],
        [ 0, 2 ],
        [ 0, 0 ]
    ]

    coordinates3 = [
        [ 1, 1 ],
        [ 3, 1 ],
        [ 3, 3 ],
        [ 1, 3 ],
        [ 1, 1 ]
    ]

    rect = GeoRectangle(coordinates2)
    rect2 = GeoRectangle(coordinates3)

    polygon2 = rect.get_overlap_polygon(rect2)
    print('tests done')
