from Evaluation import GeoJsonWriter, WordEvaluation
from Geometry.Polygon import Polygon
from Evaluation import MatchingHelper
import copy


__author__ = 'Tan'


def find_result_ground_truth_correspondence(gt_list, result_rect_list, area_threshold=0.7):
    # The json file records the overlap areas.
    overlap_json = GeoJsonWriter.init_output_json_structure()
    # The json file records the rectangles which we don't consider them as correct ones.
    non_overlap_json = GeoJsonWriter.init_output_json_structure()

    correct_results = set()
    matching_lists = []        # Records the result matching to which ground truths.

    # Find the correct and incorrect bounding boxes.
    for k in range(0, len(result_rect_list)):
        rect = result_rect_list[k]
        result_area = rect.get_area()
        matching_list = []


        for i in range(0, len(gt_list), 1):
            gt_rect_list = gt_list[i]['rects']
            for j in range(0, len(gt_rect_list), 1):
                gt_rect = gt_rect_list[j]
                gt_area = gt_rect.get_area()

                overlap_polygon = rect.get_overlap_polygon(gt_rect)
                if overlap_polygon is None:
                    pass
                else:
                    overlap_area = overlap_polygon.get_area()
                    overlap_valid = False

                    if overlap_area > area_threshold * gt_area or overlap_area > area_threshold * result_area:

                        overlap_valid = True
                        rect.positive = True
                        gt_list[i]['found'][j] = True
                        matching_list.append((i, j))
                        gt_list[i]['matching'][j].append(k)
                        correct_results.add(rect)

                    new_feature = GeoJsonWriter.generate_overlap_feature(overlap_polygon, overlap_valid, tag=i)
                    overlap_json['features'].append(new_feature)

        matching_lists.append(matching_list)

    # Record the incorrect rectangles.
    for i in range(0, len(result_rect_list)):
        rect = result_rect_list[i]
        if not rect.positive:
            non_overlap_json['features'].append(GeoJsonWriter.generate_overlap_feature(Polygon(rect.points), False, i))

    return matching_lists, correct_results, overlap_json, non_overlap_json


def evaluation_simple(result_rect_list, gt_list, area_threshold=0.7, group_para=0):
    # The json file records the overlap areas.
    overlap_json = GeoJsonWriter.init_output_json_structure()
    # The json file records the rectangles which we don't consider them as correct ones.
    non_overlap_json = GeoJsonWriter.init_output_json_structure()

    correct_results = set()

    # Find the correct and incorrect bounding boxes.
    for k in range(0, len(result_rect_list)):
        rect = result_rect_list[k]
        result_area = rect.get_area()

        gt_list_backup = copy.copy(gt_list)
        result_rect_list_backup = copy.copy(result_rect_list)
        is_invalid = False

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

                    if overlap_area >= area_threshold * gt_area or overlap_area >= area_threshold * result_area:
                        if result_area > 5 * gt_area:
                            is_invalid = False
                            break
                            # pass

                        overlap_valid = True
                        rect.positive = True
                        gt_list[i]['found'][j] = True
                        correct_results.add(rect)

                        gt_list[i]['rects'][j].text = gt_list[i]['rects'][j].text.replace(".", "")
                        result_rect_list[k].text = result_rect_list[k].text.replace(".", "")

                        ret, gt_mlist, result_mlist = WordEvaluation.levenshtein_distance(gt_list[i]['rects'][j].text,
                                                                                          result_rect_list[k].text)

                        for m in range(0, len(gt_mlist)):
                            gt_list[i]['rects'][j].textFound[m] = gt_list[i]['rects'][j].textFound[m] or gt_mlist[m]

                        for r in range(0, len(result_mlist)):
                            rect.textFound[r] = rect.textFound[r] or result_mlist[r]
                            rect.textGroup[r].append(int(gt_list[i]['rects'][j].groupId))

                        new_feature = GeoJsonWriter.generate_overlap_feature(overlap_polygon, overlap_valid, tag=i)
                        overlap_json['features'].append(new_feature)
                        rect.groundTruth.append(gt_rect.text)

        if is_invalid:
            print('Invalid roll back.')
            gt_list = gt_list_backup
            result_rect_list = result_rect_list_backup
            break

    # Compute the precision and recall
    precision_list = []
    recall_list = []
    total_extracted_characters_list = []
    total_gt_characters_list = []

    total_gt_characters = total_extracted_characters = 0
    correct_result_characters = correct_gt_characters = 0

    for r in result_rect_list:
        # print(r.text)
        for i in range(0, len(r.text)):
            if group_para in r.textGroup[i] or group_para == 0:
                if r.textFound[i]:
                    # print(r.text[i])
                    correct_result_characters += 1
                total_extracted_characters += 1
            elif len(r.textGroup[i]) == 0:
                total_extracted_characters += 1

    # print("\nGround truth")
    for i in range(0, len(gt_list), 1):
        gt_rect_list = gt_list[i]['rects']
        for j in range(0, len(gt_rect_list), 1):
            if group_para == int(gt_list[i]['rects'][j].groupId) or group_para == 0:
                gt_rect = gt_rect_list[j]
                # print(gt_rect.text)
                for k in gt_rect.textFound:
                    if k:
                        correct_gt_characters += 1
                    total_gt_characters += 1

    recall = 0 if total_gt_characters == 0 else (float(correct_gt_characters) / total_gt_characters)
    precision = 0 if total_extracted_characters == 0 else (float(correct_result_characters) / total_extracted_characters)

    print("Detected Bounding Boxes: %d" % len(result_rect_list))
    print("Correct Bounding Boxes:  %d" % len(correct_results))
    print("Number of ground truth characters: %d" % total_gt_characters)
    print("Number of detected characters:     %d" % total_extracted_characters)
    print("Number of correct detetected char: %d" % correct_result_characters)
    print("Text Recognition Precision:        %f" % precision)
    print("Text Recognition Recall:           %f" % recall)

    precision_list.append(precision)
    recall_list.append(recall)
    total_extracted_characters_list.append(total_extracted_characters)
    total_gt_characters_list.append(total_gt_characters)

    return overlap_json, non_overlap_json, precision_list, recall_list, total_extracted_characters_list, total_gt_characters_list


def evaluation(result_rect_list, gt_list):
    print("Merging method.")
    matching_lists, correct_results, overlap_json, non_overlap_json = \
        find_result_ground_truth_correspondence(gt_list, result_rect_list)

    print("Number of detected bounding boxes: %d" % len(result_rect_list))
    print("Number of correct bounding boxes:  %d" % len(correct_results))

    # Calculate precision and recall for the words.
    total_delete = total_editing = 0
    gt_count = result_count = 0
    visited_gt = []
    temp = 0
    for i in range(0, len(gt_list), 1):
        gt_rect_list = gt_list[i]['rects']
        for j in range(0, len(gt_rect_list), 1):
            temp += 1
            # Find all the matching ground truths and results.
            if (i, j) in visited_gt:
                continue

            ret = MatchingHelper.find_matching(gt_list, matching_lists, (i, j))

            # Determine the merging order of ground truths.
            ground_truths = ret[0]
            for k in range(0, len(ground_truths)):
                gt = ground_truths[k]
                ground_truths[k] = (gt[0], gt[1], gt_list[i]['rects'][0].get_center())
                visited_gt.append((gt[0], gt[1]))
                if k == 0:
                    orientation = gt_list[i]['orientation']
            ground_truths = sorted(ground_truths, key=MatchingHelper.ground_truth_key)

            if len(ground_truths) > 1:
                ground_truths, orientation = MatchingHelper.merge_ground_truth(ground_truths, gt_list)

            # Determine the merging order of results.
            results = ret[1]
            if len(results) > 1:
                results = MatchingHelper.merge_result(results, result_rect_list, orientation)

            # Merge the result string and the ground truth string.
            gt_str = ""
            for gt in ground_truths:
                gt_str = gt_str + gt_list[gt[0]]['rects'][gt[1]].text
            # gt_str = gt_str[:-1]

            result_str = ""
            for r in results:
                result_str = result_str + result_rect_list[r].text
            # print("%d to %d." % (len(ground_truths), len(results)))
            # print("Ground truth string: %s" % gt_str)
            # print("Result string:       %s" % result_str)
            # Calculate the precision and recall.
            ret, gt_mlist, result_mlist = WordEvaluation.levenshtein_distance(gt_str, result_str)
            # m_str = ""
            # for e in gt_mlist:
            #     if not e:
            #         m_str += "F"
            #     else:
            #         m_str += "T"
            # print("matching:            %s" % m_str)
            # print("add: %d, delete: %d, editing: %d" % (ret[1], ret[2], ret[3]))
            total_delete += ret[2]
            total_editing += ret[3]

            gt_count += len(gt_str)
            result_count += len(result_str)

    total_result_count = 0
    for r in result_rect_list:
        total_result_count += len(r.textFound)

    # print("Visited GT number: %d and %d" % (len(visited_gt), temp))
    print("Number of ground truth characters: %d" % gt_count)
    print("Number of detected characters:     %d" % total_result_count)

    cost = total_editing + total_delete
    precision = float(total_result_count - (total_result_count - result_count + cost)) / total_result_count
    recall = float(result_count - cost) / gt_count

    print("Text Recognition Precision:        %f" % precision)
    print("Text Recognition Recall:           %f" % recall)

    return overlap_json, non_overlap_json
