import argparse
import json
import os
from datetime import datetime

from annotation_predictor.groundtruth_reader import GroundTruthReader
from annotation_predictor.util import compute_label
from annotation_predictor.settings import alpha, annotation_predictor_metadata_dir, \
    class_ids_oid_file

evaluation_record = {}

def create_evaluation_record(path_to_detection_record: str, path_to_gt: str):
    with open(class_ids_oid_file) as f:
        class_ids_oid = json.load(f)
    for cls in class_ids_oid:
        evaluation_record.update({cls: [0,0]})

    gt_reader = GroundTruthReader(path_to_gt)
    with open(path_to_detection_record) as file:
        detections = json.load(file)

    for image_id in detections:
        gt = gt_reader.get_ground_truth_annotation(image_id)
        for det in detections[image_id]:
            cls = det['LabelName']
            label = compute_label(det, gt, alpha)
            evaluation_record[cls][0] += 1
            evaluation_record[cls][1] += label

    for i in evaluation_record:
        record = evaluation_record[i]
        if record[0] == 0:
            evaluation_record[i] = 0
        else:
            evaluation_record[i] = record[1] / record[0]

    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    path_to_json = os.path.join(annotation_predictor_metadata_dir,
                                '{}_evaluation.json'.format(timestamp))
    with open(path_to_json, 'w') as f:
        json.dump(evaluation_record, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create and save an evaluation record for the object detection network')
    parser.add_argument('path_to_detection_record', type=str, metavar='path_to_images',
                        help='path to detection record')
    parser.add_argument('--path_to_gt', type=str,
                        help='path to ground truth data', required=True)
    args = parser.parse_args()

    create_evaluation_record(args.path_to_detection_record, args.path_to_gt)
