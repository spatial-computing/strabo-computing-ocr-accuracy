from Evaluation import GeoJsonReader, GeoJsonWriter
from Evaluation import ResultEvaluation
import sys
import csv, time


__author__ = 'Tan'


def evaluate_result(gt_obj, result_obj, group_para=0, scale_w=1, scale_h=1):
    gt_list = GeoJsonReader.get_ground_truth_list(gt_obj, scale_w, scale_h)
    result_rect_list = GeoJsonReader.get_result_rectangles(result_obj)
    return ResultEvaluation.evaluation_simple(result_rect_list, gt_list, area_threshold=0.6, group_para=group_para)


if __name__ == '__main__':
    csv_file = open('evaluation_pngbypixels' + str(time.time()) + '.csv', 'w', newline="")
    csv_head = ['name', 'resolution', 'group', 'extracted char', 'gt char', 'precision', 'recall', 'f-score']
    csv_writer = csv.DictWriter(csv_file, csv_head)
    csv_writer.writerow({'name': 'name', 'resolution': 'resolution', 'group': 'group', 'precision': 'precision',
                         'recall': 'recall', 'f-score': 'f-score', 'extracted char': 'extracted char', 'gt char': 'gt char'})

    if len(sys.argv) == 1:
        print("Usage: python strabo_eval.py GT.geojson RESULT.geojson GROUP_PARA")
        exit(-1)
        # 1920 test maps
        file_list = ['1920-1', '1920-2', '1920-3', '1920-4', '1920-5', '1920-6', '1920-7',
                     '1920-8', '1920-9', '1920-10', '1', '2', '3', '4', '5']

        resolutions = [-1, 1, 0.6, 0.5]
        resolution_name = ['original', '1000-1512', '750-1512']
        resolutions[3] = float(750) / 1512
        resolutions[2] = float(1000) / 1512

        for r in range(1, 4):
            for i in range(0, len(file_list)):
                groundTruthFile = './GroundTruths/' + file_list[i] + '.geojson'
                resultFile = './Results/res' + str(r) + '/' + file_list[i] + '.pngByPixels.txt'
                print("Ground Truth: %s\nResult:       %s" % (groundTruthFile, resultFile))
                print("Scaling: %f" % (resolutions[r]))
                result_obj = GeoJsonReader.load_json_file(resultFile)
                gt_obj = GeoJsonReader.load_json_file(groundTruthFile)
                overlap_json, non_overlap_json, precision_list, recall_list, extracted_num_list, gt_num_list = \
                    evaluate_result(gt_obj, result_obj, group_para=0, scale_w=resolutions[r], scale_h=resolutions[r])
                GeoJsonWriter.output_json_file(overlap_json, 'eval_overlap_' + '_' + str(r) + '_' + resultFile.split('/')[-1])
                # GeoJsonWriter.output_json_file(non_overlap_json, 'eval_nonoverlap' + str(g) + '_' + resultFile.split('/')[-1], False)

                for u in range(0, 3):
                    gt_num = gt_num_list[u]
                    extracted_num = extracted_num_list[u]
                    precision = precision_list[u]
                    recall = recall_list[u]
                    f_score = 0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
                    csv_writer.writerow({'name': file_list[i], 'resolution': resolution_name[r - 1], 'group': str(u+1), 'precision': str(precision),
                                         'recall': str(recall), 'f-score': str(f_score), 'extracted char': extracted_num,
                                         'gt char': gt_num})
                print("")
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
