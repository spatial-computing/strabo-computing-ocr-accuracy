import csv
from Evaluation import GeoJsonReader, WordEvaluation
from Geometry.ResultRectangle import *
import cgs
import cand_valid_filter
from time import sleep


if __name__ == '__main__':
    # Read in the top score candidates.
    result_file = open('top_scores_valid.csv', 'r')
    nearby_text_file = open('near_by_3.csv', 'w')

    writer = csv.writer(nearby_text_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    rows = csv.reader(result_file, delimiter=',', quotechar='|')

    # Read in candidates.
    map_cands = {}
    for r in rows:
        mn = r[0]
        if mn not in map_cands:
            map_cands[mn] = []

        map_cands[mn].append(r)

    MAP_NUM = 11

    map_feature_list = []
    map_result_obj_features = []
    map_result_feature_count = []
    map_result_rects = []

    # Read in the result the rectangles.
    count = 0
    for i in range(1, MAP_NUM):
        map_result_rects = []
        result_file_name = './narges result/1920-' + str(i) + '.png_EdditedByPixels.txt'
        result_obj = GeoJsonReader.load_json_file(result_file_name)

        for feature in result_obj['features']:
            feature['gtFound'] = ''
            map_result_obj_features.append(feature)
            count += 1

        map_result_feature_count.append(count)

        print('Processing: ' + result_file_name)

        # Read in the features in the result file.
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

        # Find the matching rectangles for each candidates.
        mn = '1920-' + str(i) + '.png'
        cand_list = map_cands[mn]

        for cand in cand_list:
            cand_rect = None

            # Find the rect for cand.
            for rect in map_result_rects:
                x, y, w, h = rect.get_xywh()
                if x == int(cand[4]) and y == int(cand[5]) and w == int(cand[6]) and h == int(cand[7]):
                    cand_rect = rect
                    break

            # Find the nearby rects.
            dist_list = []
            for rect in map_result_rects:
                if rect == cand_rect:
                    continue

                dist = rect.get_polygon_distance(cand_rect)
                dist_list.append((dist, rect.text))

            dist_list.sort(key=lambda a: a[0])
            near_by_words = []
            for e in dist_list:
                if any(char.isdigit() for char in e[1]):
                    continue

                if any(char == ' ' for char in e[1]):
                    continue

                if len(e[1]) < 4:
                    continue

                if cand_valid_filter.verifyWord(e[1]):
                    near_by_words.append(e[1])
                    if len(near_by_words) == 2:
                        break

            # near_by_words.append(dist_list[0][1])
            # near_by_words.append(dist_list[1][1])

            search_words = '"' + cand[2] + '"'
            for w in near_by_words:
                search_words += ' AND ' + '"' + w + '"'

            count = cgs.get_pop(search_words)

            if len(near_by_words) > 0:
                cand.append(near_by_words[0])
            if len(near_by_words) > 1:
                cand.append(near_by_words[1])
            cand.append(count)

            writer.writerow(cand)

            sleep(60)

    result_file.close()
    nearby_text_file.close()