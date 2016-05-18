import csv,json
from Geometry.ResultRectangle import *
from Evaluation import GeoJsonReader


if __name__ == '__main__':
    score_file = open('scores.csv')
    score_reader = csv.reader(score_file, delimiter=',', quotechar='|')

    map_aligned_list = [[] for i in range(11)]
    map_max_scores = [[] for i in range(11)]
    map_words_locations = [[] for i in range(11)]
    map_org_texts = [[] for i in range(11)]
    map_discard_list = [[] for i in range(11)]

    for row in score_reader:
        map_name = row[0]
        if map_name.find('.png') != -1:
            org_text, aligned, score = row[1 : 4]
            map_id = int(map_name.split('-')[1].split('.')[0])
            x, y, w, h = row[4:]
            x = float(x)
            y = float(y)
            w = float(w)
            h = float(h)
            y *= -1
            h *= -1

            coordinates = [[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y]]
            temp_rect = ResultRectangle(coordinates, org_text)

            matchFound = False
            sub = -1
            for i, rect in enumerate(map_words_locations[map_id]):
                if temp_rect.is_the_same_rect(rect):
                    matchFound = True
                    sub = i
                    break

            if not matchFound:
                # add new rect
                map_words_locations[map_id].append(temp_rect)
                map_max_scores[map_id].append(score)
                map_aligned_list[map_id].append([aligned])
                map_org_texts[map_id].append(org_text)
                map_discard_list[map_id].append([])
            else:
                # compare score
                if map_max_scores[map_id][sub] < score:
                    map_max_scores[map_id][sub] = score
                    map_discard_list[map_id][sub] = map_discard_list[map_id][sub] + map_aligned_list[map_id][sub]
                    map_aligned_list[map_id][sub] = []
                    map_aligned_list[map_id][sub].append(aligned)
                elif map_max_scores[map_id][sub] == score:
                    map_aligned_list[map_id][sub].append(aligned)

    gt_list = []
    map_name = ['1920-1.png', '1920-2.png', '1920-3.png', '1920-4.png', '1920-5.png',
                '1920-6.png', '1920-7.png', '1920-8.png', '1920-9.png', '1920-10.png']


    found_gt_num = 0
    correct_num = 0
    discard_num = 0
    strabo_num = 0

    for m in range(1, 11):
        groundTruthFile = './GroundTruths/' + map_name[m-1].split('.')[0] + '.geojson'
        result_file = './rsh_rs/' + map_name[m-1] + 'ByPixels.txt'

        result_obj = GeoJsonReader.load_json_file(result_file)
        result_rect_list = GeoJsonReader.get_result_rectangles(result_obj)

        gt_obj = GeoJsonReader.load_json_file(groundTruthFile)
        gt_list = GeoJsonReader.get_ground_truth_list(gt_obj, 1, 1)

        word_locations = map_words_locations[m]
        for idw, rect in enumerate(word_locations):
            word_list = map_aligned_list[m][idw]
            discard_list = map_discard_list[m][idw]

            result_text = ''
            rect_idx = 0
            for result_rect in result_rect_list:
                if result_rect.is_the_same_rect(rect):
                    result_text = result_rect.text
                    break
                rect_idx += 1

            for i in range(0, len(gt_list), 1):
                gt_rect_list = gt_list[i]['rects']
                for j in range(0, len(gt_rect_list)):
                    gt_rect = gt_rect_list[j]
                    gt_area = gt_rect.get_area()

                    overlap_polygon = rect.get_overlap_polygon(gt_rect)
                    if overlap_polygon is None:
                        pass
                    else:
                        overlap_area = overlap_polygon.get_area()
                        overlap_valid = False
                        gt_area = gt_rect.get_area()
                        result_area = rect.get_area()

                        if overlap_area >= 0.6 * gt_area or overlap_area >= 0.6 * result_area:
                            correct_num += 1
                            # print('ground truth: ' + gt_list[i]['rects'][j].text)
                            # print('original text: ' + map_org_texts[m][idw])
                            # print(word_list)
                            found_gt = False

                            for w in word_list:
                                if w == gt_list[i]['rects'][j].text:
                                    found_gt_num += 1
                                    print('gt Found!')
                                    print('ground truth: ' + gt_list[i]['rects'][j].text)
                                    print('original text: ' + map_org_texts[m][idw])
                                    print('map name: %s, rect: %s' % (map_name[m-1], str(rect)))
                                    result_obj['features'][rect_idx]['gtf'] = 1
                                    found_gt = True
                                    break

                            if not found_gt:
                                for w in discard_list:
                                    if w == gt_list[i]['rects'][j].text:
                                        # print('Found gt in discarded word list.')
                                        discard_num += 1
                                        break

                            if result_text == gt_list[i]['rects'][j].text:
                                strabo_num += 1

                            # print(' ')
        json_result_file = open('./rsh_rs/' + map_name[m-1] + '-md.geojson', 'w')
        content = json.dumps(result_obj)
        json_result_file.write(content)
        json_result_file.close()

    print('Strabo found: ', strabo_num)
    print('Found gt in top score:', found_gt_num)
    print('Found gt in discarded word list:', discard_num)
    print('total: ', correct_num)


