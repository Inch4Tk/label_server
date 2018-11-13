import argparse
import json
import os
from datetime import datetime

from annotation_predictor.util.oid_classcode_reader import OIDClassCodeReader
from settings import annotation_predictor_metadata_dir, \
    known_class_ids_annotation_predictor

evaluation_record = {}

def create_evaluation_record(path_to_detection_record: str):
    """
    Create and save a record which represents the performance of an object-detector for each class
    of the Open Images Dataset.
    Args:
        path_to_detection_record: detection-record created by create_detection_record.py
    """
    oid_classcode_reader = OIDClassCodeReader()
    with open(known_class_ids_annotation_predictor) as f:
        class_ids_oid = json.load(f)
    for cls in class_ids_oid:
        evaluation_record.update({class_ids_oid[cls]: [0, []]})

    with open(path_to_detection_record) as file:
        detections = json.load(file)

    for image_id in detections:
        for det in detections[image_id]:
            cls = oid_classcode_reader.get_human_readable_label_for_code(det['LabelName'])
            score = det['Confidence']
            if evaluation_record[cls][0] < score:
                evaluation_record[cls][0] = score
            evaluation_record[cls][1].append(score)

    for i in evaluation_record:
        record = evaluation_record[i]
        if len(record[1]) == 0:
            record[1] = 0.0
        else:
            record[1] = sum(record[1]) / len(record[1])

    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    path_to_json = os.path.join(annotation_predictor_metadata_dir,
                                '{}_evaluation.json'.format(timestamp))
    with open(path_to_json, 'w') as f:
        json.dump(evaluation_record, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create and save an evaluation record for the object detection network')
    parser.add_argument('path_to_detection_record', type=str, metavar='path_to_detection_record',
                        help='path to detection record')
    args = parser.parse_args()

    create_evaluation_record(args.path_to_detection_record)
