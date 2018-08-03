import argparse
import json
import os
import random

from annotation_predictor.groundtruth_reader import GroundTruthReader
from annotation_predictor.util import compute_feature_vector, compute_label
from annotation_predictor.settings import alpha

def create_training_record(data_path: str, path_to_gt: str, ratio: float):
    """
    Postprocess a detection-record in order to easily use it for training a predictor
    with accept_prob_predictor.py
    Args:
        data_path: Path to detection data created by create_detection_record.py
        path_to_gt: Path to ground-truth for the images of the detection data.
        ratio: Ratio of test-images which will be separated from the training-images.
    """
    with open(data_path) as file:
        data = json.load(file)
    keys = list(data.keys())
    random.shuffle(keys)
    test_data = {}

    for i, key in enumerate(keys):
        if i > (len(keys) * ratio):
            break
        test_data.update({key: data[key]})
        data.pop(key)
    basename = os.path.splitext(os.path.basename(data_path))[0]
    base = os.path.join(os.path.dirname(data_path), basename)
    path_to_feature_data_train = '{}_{}'.format(base, 'features_train.txt')
    path_to_label_data_train = '{}_{}'.format(base, 'labels_train.txt')
    path_to_feature_data_test = '{}_{}'.format(base, 'features_test.txt')
    path_to_label_data_test = '{}_{}'.format(base, 'labels_test.txt')

    gt_reader = GroundTruthReader(path_to_gt)
    feature_data_train, label_data_train = compute_features(data, gt_reader)
    feature_data_test, label_data_test = compute_features(test_data, gt_reader)

    feature_data_ones = []
    for i, label in enumerate(label_data_train):
        if label == 1:
            feature_data_ones.append(feature_data_train[i])

    zero_offset = label_data_train.count(0) - label_data_train.count(1)
    while zero_offset > 0:
        for f in feature_data_ones:
            if zero_offset == 0:
                break
            feature_data_train.append(f)
            label_data_train.append(1.0)
            zero_offset -= 1

    with open(path_to_feature_data_train, 'w') as f:
        json.dump(feature_data_train, f)
    with open(path_to_label_data_train, 'w') as f:
        json.dump(label_data_train, f)
    with open(path_to_feature_data_test, 'w') as f:
        json.dump(feature_data_test, f)
    with open(path_to_label_data_test, 'w') as f:
        json.dump(label_data_test, f)

def compute_features(data: dict, gt_reader: GroundTruthReader):
    """
    Args:
        data: object-detection-data
        gt_reader: ground-truth-data corresponding to object-detection-data

    Returns: feature_vectors for each detection and corresponding label

    """
    feature_data = []
    label_data = []
    for key in data:
        gt = gt_reader.get_ground_truth_annotation(key)
        for i, _ in enumerate(data[key]):
            feat = compute_feature_vector(data[key], i)
            lab = compute_label(data[key][i], gt, alpha)
            feature_data.append(feat)
            label_data.append(lab)
    return feature_data, label_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Split a detection record in training and test data')
    parser.add_argument('--path_to_detections', type=str, metavar='path_to_detections',
                        help='path to detection data', required=True)
    parser.add_argument('--path_to_gt', type=str,
                        help='path to ground truth data', required=True)
    parser.add_argument('--ratio', type=float, help='ratio of test vs. training data', default=0.2)
    args = parser.parse_args()

    create_training_record(args.path_to_detections, args.path_to_gt, args.ratio)
