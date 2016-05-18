import csv
from Geometry.ResultRectangle import *
from Evaluation import GeoJsonReader
from Evaluation import ResultEvaluation

def get_result_rectangles2(geojson_obj):
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


if __name__ == '__main__':
    map_name = ['1920-1.png', '1920-2.png', '1920-3.png', '1920-4.png', '1920-5.png',
                '1920-6.png', '1920-7.png', '1920-8.png', '1920-9.png', '1920-10.png']

    csvwrite = open('Log.csv', 'w')
    fieldnames = ['map_name', 'coordinates', 'text', 'flag', 'ground_truth', 'count']
    writer = csv.DictWriter(csvwrite, fieldnames=fieldnames)
    writer.writeheader()

    csvwrite2 = open('Log2.csv', 'w')
    writer2 = csv.DictWriter(csvwrite2, fieldnames=fieldnames)
    writer2.writeheader()

    for i in range(0, 10):
        mn = map_name[i]
        print('eval ', mn)
        with open('./scores.csv') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')

            prev_result_file = './rsh_rs/' + map_name[i] + 'ByPixels.txt'
            groundTruthFile = './GroundTruths/' + map_name[i].split('.')[0] + '.geojson'

            prev_result_obj = GeoJsonReader.load_json_file(prev_result_file)
            gt_obj = GeoJsonReader.load_json_file(groundTruthFile)

            gt_list = GeoJsonReader.get_ground_truth_list(gt_obj, 1, 1)
            prev_result_rect_list = GeoJsonReader.get_result_rectangles(prev_result_obj)

            print('First eval')
            overlap_json, non_overlap_json, precision_list, recall_list, extracted_num_list, gt_num_list = \
            ResultEvaluation.evaluation_simple(prev_result_rect_list, gt_list, area_threshold=0.6, group_para=0)

            # final_list = []
            delete_list = []

            for j, rect in enumerate(prev_result_rect_list):
                found_reverse = False
                for k, rect2 in enumerate(prev_result_rect_list):
                    if j >= k:
                        continue

                    if rect.is_the_same_rect(rect2):
                        sum1 = 0
                        for f in rect.textFound:
                            sum1 += f

                        sum2 = 0
                        for f in rect2.textFound:
                            sum2 += f

                        if sum1 > sum2:
                            delete_list.append(k)
                        else:
                            delete_list.append(j)

            new_list = []
            for (j, e) in enumerate(prev_result_rect_list):
                if j in delete_list:
                    continue
                sum1 = 0
                for f in e.textFound:
                    sum1 += f
                writer.writerow({'map_name': mn, 'coordinates': str(e).replace(',', ' ').replace('\n', ''), 'text': e.text.replace(',', ' '), 'flag': str(e.textFound).replace(',', ' '),
                'ground_truth': str(e.groundTruth).replace('\n', '').replace(',', ' '), 'count': sum1})
                new_list.append(e)
            prev_result_rect_list = new_list


            overlap_json, non_overlap_json, precision_list, recall_list, extracted_num_list, gt_num_list = \
            ResultEvaluation.evaluation_simple(prev_result_rect_list, gt_list, area_threshold=0.6, group_para=0)

            # print('prev eval done')

            groundTruthFile = './GroundTruths/' + map_name[i].split('.')[0] + '.geojson'
            prev_result_obj = GeoJsonReader.load_json_file(prev_result_file)

            print('rsh eval')
            result_rect_list = []
            result_text_score_list = []
            org_text = []

            for row in reader:
                if row[0] == map_name[i]:
                    score = row[3]
                    x = int(row[4])
                    y = int(row[5]) * -1
                    w = int(row[6])
                    h = int(row[7]) * -1
                    text = row[2]
                    coordinates = [[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y]]

                    temp_rt = ResultRectangle(coordinates, text)

                    no_matching = True

                    j = 0
                    for rt in result_rect_list:
                        if rt.is_the_same_rect(temp_rt):
                            no_matching = False

                            if result_text_score_list[j] < score:
                                rt.text = text
                                result_text_score_list[j] = score
                                no_matching = False
                                rt.textFound = [False] * len(rt.text)
                                rt.textGroup = []
                                for j in range(0, len(rt.text)):
                                    rt.textGroup.append([])
                                break

                        j += 1

                    if no_matching:
                        result_rect_list.append(temp_rt)
                        result_text_score_list.append(score)
                        org_text.append(row[1])

            print('read in result rect')

            to_add = []
            for rect in result_rect_list:
                found_matched = False
                for prev_rect in prev_result_rect_list:
                    if prev_rect.is_the_same_rect(rect) and prev_rect.text == rect.text:
                        found_matched = True
                        prev_rect.text = rect.text
                        prev_rect.textFound = [False] * len(prev_rect.text)
                        prev_rect.textGroup = []
                        for j in range(0, len(prev_rect.text)):
                            prev_rect.textGroup.append([])

                if not found_matched:
                    to_add.append(rect)

            for e in to_add:
                print("add")
                prev_result_rect_list.append(e)

            groundTruthFile = './GroundTruths/' + map_name[i].split('.')[0] + '.geojson'
            prev_result_obj = GeoJsonReader.load_json_file(prev_result_file)

            overlap_json, non_overlap_json, precision_list, recall_list, extracted_num_list, gt_num_list = \
            ResultEvaluation.evaluation_simple(prev_result_rect_list, gt_list, area_threshold=0.6, group_para=0)

            delete_list = []

            for j, rect in enumerate(prev_result_rect_list):
                found_reverse = False
                for k, rect2 in enumerate(prev_result_rect_list):
                    if j >= k:
                        continue

                    if rect.is_the_same_rect(rect2):
                        sum1 = 0
                        for f in rect.textFound:
                            sum1 += f

                        sum2 = 0
                        for f in rect2.textFound:
                            sum2 += f

                        if sum1 > sum2:
                            delete_list.append(k)
                        else:
                            delete_list.append(j)

            new_list = []
            for (j, e) in enumerate(prev_result_rect_list):
                if j in delete_list:
                    continue
                sum1 = 0
                for f in e.textFound:
                    sum1 += f
                writer2.writerow({'map_name': mn, 'coordinates': str(e).replace('\n', '').replace(',', ' '), 'text': e.text.replace(',', ' '), 'flag': str(e.textFound).replace(',', ' '),
                'ground_truth': str(e.groundTruth).replace('\n', '').replace(',', ' '), 'count': sum1})
                new_list.append(e)
            prev_result_rect_list = new_list


            overlap_json, non_overlap_json, precision_list, recall_list, extracted_num_list, gt_num_list = \
            ResultEvaluation.evaluation_simple(prev_result_rect_list, gt_list, area_threshold=0.6, group_para=0)

            print('rsh done')

    csvwrite.close()
    csvwrite2.close()