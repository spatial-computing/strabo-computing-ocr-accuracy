from Geometry.Orientation import Orientation
import math
import numpy as np


def find_matching(gt_list, result_matching_list, index):
    results = gt_list[index[0]]['matching'][index[1]]
    ground_truths = []

    visited_gt = [index]
    visited_result = []

    while len(results) != 0 or len(ground_truths) != 0:
        if len(results) != 0:
            for r in results:
                visited_result.append(r)
                gts = result_matching_list[r]
                for gt in gts:
                    if gt not in visited_gt:
                        ground_truths.append(gt)
            results = []
        else:
            for g in ground_truths:
                gt_results = gt_list[g[0]]['matching'][g[1]]
                visited_gt.append(g)
                for r in gt_results:
                    if r not in visited_result:
                        results.append(r)
            ground_truths = []

    return visited_gt, visited_result


def merge_ground_truth(matching_gts, gt_list):
    center_x = []
    center_y = []
    orientations = [0, 0, 0, 0]
    sort_list = []
    for gt in matching_gts:
        center = gt_list[gt[0]]['rects'][gt[1]].get_center()
        center_x.append(center[0])
        center_y.append(center[1])
        dirction = gt_list[gt[0]]['orientation']
        orientations[dirction] += 1
        sort_list.append((center_x, center_y, gt))

    A = np.vstack([center_x, np.ones(len(center_x))]).T
    k, b = np.linalg.lstsq(A, center_y)[0]

    if 0 <= k <= 1 or -1 <= k <= 0:
        # connect the ground truth from left to right.
        sorted(sort_list, key=lambda a: a[0])
        orientation = Orientation.LEFT2RIGHT
    else:
        # Connect the ground truth based on the orientation of ground truth.
        if orientations[Orientation.BOTTOM2TOP] > orientations[Orientation.TOP2BOTTOM]:
            sorted(sort_list, key=lambda a: a[1])
            orientation = Orientation.BOTTOM2TOP
        else:
            sorted(sort_list, key=lambda a: a[1], reverse=True)
            orientation = Orientation.TOP2BOTTOM

    matching_gts = []
    for e in sort_list:
        matching_gts.append(e[2])

    return matching_gts, orientation


def merge_result(result_list, result_rect_list, orientation):
    sort_list = []
    for r in result_list:
        rect = result_rect_list[r]
        center = rect.get_center()
        sort_list.append((center[0], center[1], r))

    if orientation == Orientation.LEFT2RIGHT:
        sorted(sort_list, key=lambda k: k[0])
    elif orientation == Orientation.BOTTOM2TOP:
        sorted(sort_list, key=lambda k: k[1])
    else:
        sorted(sort_list, key=lambda k: k[1], reverse=True)

    result_list = []
    for e in sort_list:
        result_list.append(e[2])

    return result_list


def ground_truth_key(gt):
    return math.pow(gt[2][0], 2) + math.pow(gt[2][1], 2) + float(gt[0]) / float(1000) + float(gt[1]) / float(1000000)
