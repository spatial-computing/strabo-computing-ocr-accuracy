__author__ = 'Tan'


# This is the evaluation method for text recognition.
def levenshtein_distance(ground_truth, result, add=0, delete=0, sub=0):
    DELETE_COST = 2
    EDITING_COST = 2
    INSERTION_COST = 1

    len_gt = len(ground_truth)
    len_result = len(result)

    # Each item means (cost, add, delete, sub)
    cost_matrix = [[(0, 0, 0, 0) for x in range(len_gt + 1)] for x in range(len_result + 1)]

    for i in range(0, len_gt + 1):
        cost_matrix[0][i] = (i, i, 0, 0)

    for i in range(0, len_result + 1):
        cost_matrix[i][0] = (i, 0, i, 0)

    for i in range(0, len_gt):
        for j in range(0, len_result):
            cost = 0 if ground_truth[i] == result[j] else 1

            cost_list = []
            item = cost_matrix[j + 1][i]
            cost_list.append((item[0] + INSERTION_COST, item[1] + 1, item[2], item[3]))

            item = cost_matrix[j][i + 1]
            cost_list.append((item[0] + DELETE_COST, item[1], item[2] + 1, item[3]))

            item = cost_matrix[j][i]
            cost_list.append((item[0] + cost * EDITING_COST, item[1], item[2], item[3] + cost))

            min_dist = min(cost_list, key=lambda c: float(c[0]) + float(c[2] + c[3]) / 1000)
            cost_matrix[j + 1][i + 1] = min_dist

    # Back tracking.
    j = len_result
    i = len_gt

    ground_truth_matching_list = []
    result_matching_list = []

    while i != 0 and j != 0:
        if i == 0 or j == 0:
            cost = 1
        else:
            cost = 0 if ground_truth[i - 1] == result[j - 1] else 1

        if cost_matrix[j - 1][i][0] + DELETE_COST == cost_matrix[j][i][0]:
            j -= 1
            result_matching_list.append(False)
        elif cost_matrix[j][i][0] == cost_matrix[j - 1][i - 1][0] + cost * EDITING_COST:
            # Editing or matching.
            if cost == 0:
                ground_truth_matching_list.append(True)
                result_matching_list.append(True)
            else:
                ground_truth_matching_list.append(False)
                result_matching_list.append(False)
            i -= 1
            j -= 1
        else:
            i -= 1
            ground_truth_matching_list.append(False)

    # All the characters left in ground truth are not matched.
    for k in range(0, i):
        ground_truth_matching_list.append(False)

    for k in range(0, j):
        result_matching_list.append(False)

    return cost_matrix[len_result][len_gt], list(reversed(ground_truth_matching_list)), \
           list(reversed(result_matching_list))


def get_characters_edit_distance(gt_list):
    total_edit_distance = 0

    for gt in gt_list:
        for distance in gt['recognition']:
            total_edit_distance += distance

    return float(total_edit_distance)


def get_word_precision(result_rect_list):
    total_characters = 0
    delete_and_editing = 0

    for rect in result_rect_list:
        total_characters += len(rect.text)
        delete_and_editing += rect.editing[1] + rect.editing[2]

    print('Levenshtein distance precision: ', (float(total_characters - delete_and_editing) / total_characters))


def get_word_recall(gt_list):
    total_characters = 0
    delete_and_editing = 0

    for gt in gt_list:
        rects = gt['rects']
        for j in range(0, len(rects)):
            text = rects[j].text
            total_characters += len(text)
            delete_and_editing += gt['editing'][j][1] + gt['editing'][j][2]

    print('levenshtein distance recall: %f' % (float(total_characters - delete_and_editing) / total_characters))
