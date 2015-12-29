from Evaluation import GeoJsonReader
import strabo_eval
import json


if __name__ == '__main__':
    for i in range(1, 8):
        groundTruthFile = './GroundTruths/1920_' + i.__str__() + '.geojson'
        gt_obj = strabo_eval.load_json_file(groundTruthFile)
        features = gt_obj['features']
        delete_list = [0] * len(features)
        for i in range(0, len(delete_list)):
            for j in range(i + 1, len(delete_list)):
                if delete_list[j] == 1:
                    break
                if features[i] == features[j]:
                    delete_list[j] = 1

        new_features = list()
        for i in range(0, len(delete_list)):
            if delete_list[i] == 0:
                new_features.append(features[i])

        gt_obj['features'] = new_features
        new_file = open(groundTruthFile, 'w')
        new_file.write(json.dumps(gt_obj))
        new_file.close()
