__author__ = 'Tan'


def get_detection_precision(result_rect_list):
    positive_count = 0
    for rect in result_rect_list:
        if rect.positive:
            positive_count += 1

    return float(positive_count) / len(result_rect_list)


def get_detection_recall(gt_list):
    total_word = 0
    detected_word = 0

    for gt in gt_list:
        total_word += len(gt['found'])
        for detected in gt['found']:
            if detected:
                detected_word += 1

    return float(detected_word) / total_word
