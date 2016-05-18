from Evaluation import GeoJsonReader
from Evaluation import GeoJsonWriter, WordEvaluation
from Geometry.ResultRectangle import *
import classify_gbc, csv, json, sys


if __name__ == '__main__':
    MAP_NUM = 11
    scorefile = open('./nar_score.csv', 'w')
    rect_precision_file = open('./rect_precision.csv', 'w')

    fieldnames2 = ['map_name', 'org_text', 'rsh_text', 'score', 'id', 'x', 'y', 'w', 'h']
    fieldnames = ['rect', 'precision', 'gt_recovered']

    proceed_sets = set()

    score_writer = csv.DictWriter(scorefile, fieldnames=fieldnames2)
    score_writer.writeheader()

    rect_writer = csv.DictWriter(rect_precision_file, fieldnames=fieldnames)
    rect_writer.writeheader()

    # Read Ground Truth.
    map_gt_list = [];
    for m in range(1, 11):
        map_name = ['1920-1.png', '1920-2.png', '1920-3.png', '1920-4.png', '1920-5.png',
                    '1920-6.png', '1920-7.png', '1920-8.png', '1920-9.png', '1920-10.png']

        groundTruthFile = './GroundTruths/' + map_name[m - 1].split('.')[0] + '.geojson'
        gt_obj = GeoJsonReader.load_json_file(groundTruthFile)
        gt_list = GeoJsonReader.get_ground_truth_list(gt_obj, 1, 1)
        map_gt_list.append(gt_list)

    candidate_file = './narges result/candidates'
    cf = open(candidate_file, 'r')

    map_feature_list = []
    map_result_obj_features = []
    map_result_feature_count = []
    map_result_rects = []

    # Read result files.
    count = 0
    for i in range(1, MAP_NUM):
        result_file_name = './narges result/1920-' + str(i) + '.png_EdditedByPixels.txt'
        result_obj = GeoJsonReader.load_json_file(result_file_name)

        for feature in result_obj['features']:
            feature['gtFound'] = ''
            map_result_obj_features.append(feature)
            count += 1

        map_result_feature_count.append(count)

        print('Processing: ' + result_file_name)

        for feature in result_obj['features']:
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
                map_result_rects.append(rect)
                map_feature_list.append((i, rect))
                result_area = rect.get_area()
                rect_gt_list = []

                area_threshold = 0.7
                gt_list = map_gt_list[i-1]
                for u in range(0, len(gt_list), 1):
                    gt_rect_list = gt_list[u]['rects']
                    for j in range(0, len(gt_rect_list)):
                        gt_rect = gt_rect_list[j]
                        gt_area = gt_rect.get_area()

                        overlap_polygon = rect.get_overlap_polygon(gt_rect)
                        if overlap_polygon is None:
                            pass
                        else:
                            overlap_area = overlap_polygon.get_area()
                            overlap_valid = False

                            if overlap_area >= area_threshold * gt_area or overlap_area >= area_threshold * result_area:
                                overlap_valid = True
                                rect.positive = True
                                gt_list[u]['found'][j] = True

                                rect.groundTruth.append(gt_rect.text)
                                gt_list[u]['rects'][j].text = gt_list[u]['rects'][j].text.replace(".", "")
                                rect.text = rect.text.replace(".", "")

                                ret, gt_mlist, result_mlist = WordEvaluation.levenshtein_distance(gt_list[u]['rects'][j].text,
                                                                                                  rect.text)

                                for m in range(0, len(gt_mlist)):
                                    gt_list[u]['rects'][j].textFound[m] = gt_list[u]['rects'][j].textFound[m] or gt_mlist[m]

                                for r in range(0, len(result_mlist)):
                                    rect.textFound[r] = rect.textFound[r] or result_mlist[r]
                                    rect.textGroup[r].append(int(gt_list[u]['rects'][j].groupId))
    # sys.exit(0)

    # Begin to evaluate the candidates.
    lines = cf.readlines()
    count = 0

    candidates = []
    word_score = {}

    # Compute the score for all the candidates.
    while count + 5 < len(lines):
        # print('Computing score for candiate: %d' % int(count / 6))
        original_phrase = lines[count + 1]
        original_word = lines[count + 2][:-1].replace('-', '')
        alignment0 = lines[count + 2][:-1]
        alignment1 = lines[count + 3][:-1]
        idx = int(lines[count + 4][:-1])

        score = classify_gbc.sequence2(alignment0, alignment1)

        if original_phrase not in word_score:
            word_score[original_phrase] = {}

        if original_word not in word_score[original_phrase]:
            word_score[original_phrase][original_word] = {}
            word_score[original_phrase][original_word]['max'] = -10000
            word_score[original_phrase][original_word]['cand'] = []

        dict_text = alignment1.replace('-', '')
        word_score[original_phrase][original_word]['cand'].append((idx, dict_text, score))
        if score > word_score[original_phrase][original_word]['max']:
            word_score[original_phrase][original_word]['max'] = score

        count += 6

    for phrase in word_score:
        for word in word_score[phrase]:
            max_score = word_score[phrase][word]['max']
            for cand in word_score[phrase][word]['cand']:
                idx = cand[0]
                dict_text = cand[1]
                score = cand[2]

                found_gt = False

                corresponding_rect = map_feature_list[idx]
                corresponding_feature = map_result_obj_features[idx]

                corresponding_rect[1].rsh_proceed = True

                mn = map_name[corresponding_rect[0] - 1]
                (x, y, w, h) = corresponding_rect[1].get_xywh()
                rect = map_result_rects[idx]
                for gt_text in rect.groundTruth:
                    gt_text_list = gt_text.split(' ')
                    for t in gt_text_list:
                        if t == dict_text and score == max_score:
                            found_gt = True
                            corresponding_feature['gtFound'] = corresponding_feature['gtFound'] + ' ' + dict_text
                            corresponding_rect[1].rsh_gt_found = True
                            print("map: %s, text: %s" % (mn, dict_text))

                candidates.append((idx, score, dict_text, original_word, original_phrase, found_gt))

                score_writer.writerow(
                    {'map_name': mn, 'org_text': word.replace(',', '').replace('\n', '').replace('"', ''),
                     'rsh_text': dict_text, 'score': str(score), 'id': str(idx),
                     'x': str(int(x)), 'y': str(int(y)), 'w': str(int(w)), 'h': str(int(h))})


    # Output features
    count = 0
    for i in range(1, MAP_NUM):
        temp_obj = dict()
        temp_obj['type'] = 'FeatureCollection'
        temp_obj['features'] = []

        while count < map_result_feature_count[i - 1]:
            temp_obj['features'].append(map_result_obj_features[count])
            count += 1

        name = "./rsh_rs/" + map_name[i-1] + "_score.json"
        json_result_file = open(name, 'w')
        content = json.dumps(temp_obj)
        json_result_file.write(content)
        json_result_file.close()

    # Output corresponding rects.
    for rect in map_result_rects:
        if rect.rsh_proceed:
            rect_writer.writerow({'precision': str(rect.get_text_precision()),
                                  'gt_recovered': str(rect.rsh_gt_found)})

    scorefile.close()
