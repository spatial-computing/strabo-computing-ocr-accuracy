__author__ = 'Tan'


def get_phrase_recognition_recall(gt_list):
    recall = 0

    for gt in gt_list:
        recognized = True
        for i in range(0, len(gt['recognition'])):
            if not gt['recognition'][i]:
                recognized = False
                break
        if recognized:
            recall += 1

    return float(recall) / len(gt_list)


def get_phrase_detection_recall(gt_list):
    precision = 0

    for gt in gt_list:
        recognized = True
        for i in range(0, len(gt['found'])):
            if not gt['found'][i]:
                recognized = False
                break
        if recognized:
            precision += 1

    return float(precision) / len(gt_list)
