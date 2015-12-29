from Geometry import GeoRectangle


__author__ = 'Tan'


class GroundTruthRectangle(GeoRectangle.GeoRectangle):
    def __init__(self, location, text, phrase, coordinates, groupId=0):
        self.id = location
        self.phrase = phrase
        self.groupId = groupId
        text = text.replace("\'", "")
        text = text.replace(".", "")

        GeoRectangle.GeoRectangle.__init__(self, coordinates, text)
