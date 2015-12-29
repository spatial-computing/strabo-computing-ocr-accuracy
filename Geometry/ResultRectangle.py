from Geometry import GeoRectangle


__author__ = 'Tan'


class ResultRectangle(GeoRectangle.GeoRectangle):
    def __init__(self, coordinates, text):
        self.positive = False
        self.editing = [0, 0, 0]
        self.textGroup = []
        for i in range(0, len(text)):
            self.textGroup.append([])

        text = text.replace("\'", "")
        text = text.replace(".", "")

        GeoRectangle.GeoRectangle.__init__(self, coordinates, text)
