from Geometry.ResultRectangle import *
from Geometry.GroundTruthRectangle import *
from Geometry.Orientation import Orientation
from Evaluation import ResultEvaluation
import json, math, sys


__author__ = 'Tan'


def load_json_file(filename):
    plain_text = open(filename).read()

    # Make the plain text can be recognized by the json module.
    plain_text = plain_text.replace(',}', '}')
    plain_text = plain_text.replace(',]', ']')
    plain_text = plain_text.replace('}]}]}', '}]}')
    plain_text = " ".join(plain_text.split("\n"))
    # plain_text = plain_text.replace(" ", "")

    data = json.loads(plain_text)
    return data


def get_result_rectangles(geojson_obj):
    rectangle_list = []
    for feature in geojson_obj['features']:
        if 'TextNonText' in feature:
            text = feature['TextNonText']
        else:
            if 'properties' in feature and 'text' in feature['properties']:
                text = feature['properties']['text']
            elif 'NameAfterDictionary' in feature:
                text = feature['NameBeforeDictionary']
            else:
                print('Invalid file format.')
                quit()

        if text == 'NonText':
            text = ""

        for coordinate in feature['geometry']['coordinates']:
            text = text.lower()
            rect = ResultRectangle(coordinate, text)
            rectangle_list.append(rect)

    return rectangle_list


def get_ground_truth_list(gt_obj, scale_w=1, scale_h=1):
    gt_list = []
    total_text = 0
    for feature in gt_obj['features']:
        feature['properties'] = dict((k.lower(), v) for k, v in feature['properties'].items())
        if 'label' in feature['properties']:
            feature['properties']['text'] = feature['properties'].pop('label')
        total_text += len(feature['properties']['text'])
    # print("totaol_text: %d" % total_text)

    visited_feature_set = list()
    for feature in gt_obj['features']:
        if feature['properties']['id'] == 1 or feature['properties']['id'] == '1':
            visited_feature_set.append(feature)
            new_phrase_dict = {}
            phrase = feature['properties']['phrase']
            total_words = len(phrase.split(' '))
            groupId = 0 if 'group' not in feature['properties'] else feature['properties']['group']
            new_gt_rect = GroundTruthRectangle(feature['properties']['id'], feature['properties']['text'].lower(),
                                               feature['properties']['phrase'].lower(), feature['geometry']['coordinates'][0], groupId)
            new_gt_rect.scale(scale_w, scale_h)

            new_phrase_dict['phrase'] = phrase
            new_phrase_dict['rects'] = [new_gt_rect]
            new_phrase_dict['found'] = [False]
            new_phrase_dict['matching'] = [[]]             # Recognition stroes the lists of results that contain the ground truth
            new_phrase_dict['editing'] = [(0, 0, 0, 0)]    # Editing stores the cost and operations needed to perform in Levenshtein distance.

            for i in range(2, total_words + 1, 1):
                for f2 in gt_obj['features']:
                    if f2['properties']['phrase'] == phrase and (f2['properties']['id'] == i or f2['properties']['id'] == str(i)):
                        visited_feature_set.append(f2)
                        groupId = 0 if 'group' not in f2['properties'] else f2['properties']['group']
                        new_gt_rect = GroundTruthRectangle(f2['properties']['id'], f2['properties']['text'].lower(),
                                                           f2['properties']['phrase'].lower(), f2['geometry']['coordinates'][0], groupId)
                        new_gt_rect.scale(scale_w, scale_h)

                        new_phrase_dict['rects'].append(new_gt_rect)
                        new_phrase_dict['found'].append(False)
                        new_phrase_dict['matching'].append([])
                        new_phrase_dict['editing'].append([0, 0, 0, 0])

            # Compute the orientation of this phrase.
            if len(new_phrase_dict['rects']) <= 1:
                new_phrase_dict['orientation'] = Orientation.ISOLATED
            else:
                first_rect = new_phrase_dict['rects'][0]
                last_rect = new_phrase_dict['rects'][1]

                first_center = first_rect.get_center()
                last_center = last_rect.get_center()

                delta_x = math.fabs(first_center[0] - last_center[0])
                delta_y = math.fabs(first_center[1] - last_center[1])

                if delta_x > delta_y:
                    new_phrase_dict['orientation'] = Orientation.LEFT2RIGHT
                else:
                    if first_center[1] > last_center[1]:
                        new_phrase_dict['orientation'] = Orientation.TOP2BOTTOM
                    else:
                        new_phrase_dict['orientation'] = Orientation.BOTTOM2TOP

            gt_list.append(new_phrase_dict)

    for feature in gt_obj['features']:
        if feature not in visited_feature_set:
            new_phrase_dict = {}
            phrase = feature['properties']['phrase']
            groupId = 0 if 'group' not in feature['properties'] else feature['properties']['group']
            new_gt_rect = GroundTruthRectangle(feature['properties']['id'], feature['properties']['text'].lower(),
                                               feature['properties']['phrase'].lower(), feature['geometry']['coordinates'][0], groupId)
            new_gt_rect.scale(scale_w, scale_h)

            new_phrase_dict['phrase'] = phrase
            new_phrase_dict['rects'] = [new_gt_rect]
            new_phrase_dict['found'] = [False]
            new_phrase_dict['matching'] = [[]]             # Recognition stroes the lists of results that contain the ground truth
            new_phrase_dict['editing'] = [(0, 0, 0, 0)]    # Editing stores the cost and operations needed to perform in Levenshtein distance.

            gt_list.append(new_phrase_dict)

    return gt_list


def load_result_as_ground_truth(result_obj):
    gt_list = []

    for feature in result_obj['features']:
        new_phrase_dict = dict()
        new_gt_rect = GroundTruthRectangle(1, feature['NameAfterDictionary'], feature['NameAfterDictionary'],
                                           feature['geometry']['coordinates'][0])
        new_phrase_dict['phrase'] = feature['NameAfterDictionary']
        new_phrase_dict['rects'] = [new_gt_rect]
        new_phrase_dict['orientation'] = Orientation.ISOLATED
        new_phrase_dict['matching'] = [[]]
        new_phrase_dict['found'] = ['False']
        new_phrase_dict['editing'] = [(0, 0, 0, 0)]
        gt_list.append(new_phrase_dict)

    return gt_list


if __name__ == '__main__':
    groundTruthFile = sys.argv[1]
    resultFile = sys.argv[2]
    output_file = open("../Output/matching_list.txt", "w")

    result_obj = load_json_file(resultFile)
    gt_list = load_result_as_ground_truth(result_obj)
    gt_list = list(reversed(gt_list))
    result_rect_list = get_result_rectangles(result_obj)
    ret = ResultEvaluation.find_result_ground_truth_correspondence(gt_list, result_rect_list)
    matching_lists = ret[0]

    for ml in matching_lists:
        for m in ml:
            output_str = str(m[0])
            output_file.write(output_str)
            output_file.write("\n")
        output_file.write("\n")
