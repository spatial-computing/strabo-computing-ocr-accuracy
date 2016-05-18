from Evaluation import GeoJsonReader, GeoJsonWriter
from Evaluation import ResultEvaluation
import sys
import csv, time


__author__ = 'Tan'


def evaluate_result(gt_obj, result_obj, group_para=0, scale_w=1, scale_h=1):
    gt_list = GeoJsonReader.get_ground_truth_list(gt_obj, scale_w, scale_h)
    result_rect_list = GeoJsonReader.get_result_rectangles(result_obj)
    return ResultEvaluation.evaluation_simple(result_rect_list, gt_list, area_threshold=0.7, group_para=group_para)


if __name__ == '__main__':
    csv_file = open('evaluation_pngbypixels' + str(time.time()) + '.csv', 'w', newline="")
    csv_head = ['name', 'resolution', 'group', 'extracted char', 'gt char', 'precision', 'recall', 'f-score']
    csv_writer = csv.DictWriter(csv_file, csv_head)
    csv_writer.writerow({'name': 'name', 'resolution': 'resolution', 'group': 'group', 'precision': 'precision',
                         'recall': 'recall', 'f-score': 'f-score', 'extracted char': 'extracted char', 'gt char': 'gt char'})

    if len(sys.argv) == 1:
        # print("Usage: python strabo_eval.py GT.geojson RESULT.geojson GROUP_PARA")
        # exit(-1)
        # 1920 test maps
        file_list = ['1920-1', '1920-2', '1920-3', '1920-4', '1920-5', '1920-6', '1920-7',
                     '1920-8', '1920-9', '1920-10', 'Grinnell-1', 'Grinnell-2', 'Grinnell-3', 'Grinnell-4', 'Grinnell-5']

        resolutions = [-1, 0.167, 0.33, 1.32, 1.65]
        resolution_name = ['250-1512', '500-1512', '2000-1512', '2500-1512']
        resolutions[1] = float(250) / 1512
        resolutions[2] = float(500) / 1512
        resolutions[3] = float(2000) / 1512
        resolutions[4] = float(2500) / 1512

        precisions = [ [[] for x in resolution_name] for y in range(1, 4) ]
        recalls = [ [[] for x in resolution_name] for y in range(1, 4) ]

        for r in range(1, 5):
            for i in range(0, len(file_list)):
                for u in range(1, 4):
                    groundTruthFile = './GroundTruths/' + file_list[i] + '.geojson'
                    resultFile = './Results/res' + str(r) + '/' + file_list[i] + '.pngByPixels.txt'
                    print("Ground Truth: %s\nResult:       %s" % (groundTruthFile, resultFile))
                    print("Scaling: %f" % (resolutions[r]))

                    result_obj = GeoJsonReader.load_json_file(resultFile)
                    gt_obj = GeoJsonReader.load_json_file(groundTruthFile)

                    overlap_json, non_overlap_json, precision_list, recall_list, extracted_num_list, gt_num_list = \
                    evaluate_result(gt_obj, result_obj, group_para=u, scale_w=resolutions[r], scale_h=resolutions[r])

                    gt_num = gt_num_list[0]
                    extracted_num = extracted_num_list[0]

                    precision = precision_list[0]
                    recall = recall_list[0]

                    precisions[u - 1][r - 1].append(precision)
                    recalls[u - 1][r - 1].append(recall)

                    f_score = 0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
                    csv_writer.writerow({'name': file_list[i], 'resolution': resolution_name[r - 1], 'group': str(u), 'precision': str(precision),
                                         'recall': str(recall), 'f-score': str(f_score), 'extracted char': extracted_num,
                                         'gt char': gt_num})
                print("")

        print("Group - Resolution Precision and Recall.")
        for u in range(0, 3):
            for r in range(0, 4):
                psum = 0
                rsum = 0
                count = 0
                for k in precisions[u][r]:
                    psum += k
                    count += 1
                for k in recalls[u][r]:
                    rsum += k
                p = float(psum) / float(count)
                re = float(rsum) / float(count)
                f = 2 * p * re / (p + re) if re + p != 0 else 0
                print("Group: %s, Resolution: %s, Precision: %f, Recall: %f, F-score: %f" % (str(u + 1), resolution_name[r], p, re, f))
                na = "N/A"
                csv_writer.writerow({'name': na, 'resolution': resolution_name[r], 'group': str(u + 1),
                                     'precision': str(p),
                                     'recall': str(re), 'f-score': str(f), 'extracted char': -1,
                                     'gt char': -1})

        print("Resolution - Group Precision and Recall")
        for r in range(0, 4):
            for u in range(0, 3):
                psum = 0
                rsum = 0
                count = 0
                for k in precisions[u][r]:
                    psum += k
                    count += 1
                for k in recalls[u][r]:
                    rsum += k
                p = float(psum) / float(count)
                re = float(rsum) / float(count)
                f = 2 * p * re / (p + re) if re + p != 0 else 0
                print("Resolution: %s, Group: %s, Precision: %f, Recall: %f, F-score: %f" % (resolution_name[r], str(u + 1), p, re, f))
                na = "N/A"
                csv_writer.writerow({'name': na, 'resolution': resolution_name[r], 'group': str(u + 1),
                                     'precision': str(p),
                                     'recall': str(re), 'f-score': str(f), 'extracted char': -1,
                                     'gt char': -1})

    else:
        groundTruthFile = sys.argv[1]
        resultFile = sys.argv[2]
        group_para = int(sys.argv[3])
        # TODO: Add the group parameters.
        # groupID = sys[3]
        result_obj = GeoJsonReader.load_json_file(resultFile)
        gt_obj = GeoJsonReader.load_json_file(groundTruthFile)
        overlap_json, non_overlap_json, precision_list, recall_list, extracted_num_list, gt_num_listc = evaluate_result(gt_obj, result_obj, group_para=group_para)
        # GeoJsonWriter.output_json_file(overlap_json, 'eval_overlap' + resultFile.split('/')[-1])
        # GeoJsonWriter.output_json_file(non_overlap_json, 'eval_nonoverlap' + resultFile.split('/')[-1], False)
