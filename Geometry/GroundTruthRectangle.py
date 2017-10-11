from Geometry import GeoRectangle
from Geometry import GeoPolygon


__author__ = 'Tan'


class GroundTruthRectangle(GeoPolygon.GeoPolygon):
    def __init__(self, location, text, phrase, coordinates, groupId=0):
        self.id = location
        self.phrase = phrase
        self.groupId = groupId
        text = text.replace("\'", "")
        text = text.replace(".", "")

        # GeoRectangle.GeoRectangle.__init__(self, coordinates, text)
        GeoPolygon.GeoPolygon.__init__(self, coordinates, text)
