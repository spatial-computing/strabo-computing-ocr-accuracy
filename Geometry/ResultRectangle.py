from Geometry import GeoRectangle


__author__ = 'Tan'


class ResultRectangle(GeoRectangle.GeoRectangle):
    def __init__(self, coordinates, text):
        self.positive = False
        self.editing = [0, 0, 0]
        self.textGroup = []
        self.groundTruth = []
        self.rsh_proceed = False
        self.rsh_gt_found = False
        for i in range(0, len(text)):
            self.textGroup.append([])

        text = text.replace("\'", "")
        text = text.replace(".", "")

        GeoRectangle.GeoRectangle.__init__(self, coordinates, text)

    def get_text_precision(self):
        correct = 0
        for i in range(0, len(self.text)):
            if self.textFound[i] == True:
                correct += 1

        return float(correct) / float(len(self.text))