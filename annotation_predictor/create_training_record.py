import argparse
import json
import os
import sys
from datetime import datetime

import tensorflow as tf

from annotation_predictor.util.groundtruth_reader import GroundTruthReader
from settings import alpha
from annotation_predictor.util.util import compute_feature_vector, compute_label

def create_training_record(data_path: str, path_to_gt: str, ratio: float):
    """
    Post-process a detection-record in order to easily use it for training a predictor
    with accept_prob_predictor.py
    Args:
        data_path: Path to detection data created by create_detection_record.py
        path_to_gt: Path to ground-truth for the images of the detection data.
        ratio: Ratio of test-images which will be separated from the training-images.
    """
    with open(data_path) as file:
        data = json.load(file)

    base = os.path.join(os.path.dirname(data_path), datetime.now().strftime('%Y_%m_%d_%H%M%S'))
    train_filename = '{}_{}'.format(base, 'train.tfrecords')
    test_filename = '{}_{}'.format(base, 'test.tfrecords')

    train_writer = tf.python_io.TFRecordWriter(train_filename)
    test_writer = tf.python_io.TFRecordWriter(test_filename)

    gt_reader = GroundTruthReader(path_to_gt)
    train_set_len = 1
    test_set_len = 1
    zeros = 0
    ones = 0

    for i, key in enumerate(data):
        if not i % 1000:
            print('Data: {}/{}'.format(i, len(data)))
            sys.stdout.flush()

        features, labels = compute_feature(key, data[key], gt_reader)

        for j, feat in enumerate(features):
            label = labels[j]
            if test_set_len / train_set_len >= ratio:
                # balance out training dataset (there are normally more zero- than one-labels)
                if (label == 0.0 and (zeros - ones <= 0)) or label == 1.0:
                    train_set_len += 1
                    if label == 1.0:
                        ones += 1
                    else:
                        zeros += 1
                    feature = {'train/feature': float_feature(feat),
                               'train/label': float_feature(labels[j])}
                    example = tf.train.Example(features=tf.train.Features(feature=feature))
                    train_writer.write(example.SerializeToString())
            else:
                test_set_len += 1
                feature = {'test/feature': float_feature(feat),
                           'test/label': float_feature(labels[j])}
                example = tf.train.Example(features=tf.train.Features(feature=feature))
                test_writer.write(example.SerializeToString())
    train_writer.close()
    sys.stdout.flush()

def float_feature(value):
    if type(value) is not list:
        value = [value]
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def compute_feature(image_id: str, data: list, gt_reader: GroundTruthReader):
    """
    Args:
        image_id: uniquely defines an image
        data: object-detection-data
        gt_reader: ground-truth-data corresponding to object-detection-data

    Returns: feature_vector and corresponding label

    """
    gt = gt_reader.get_ground_truth_annotation(image_id)
    feature_data = []
    label_data = []

    for i, _ in enumerate(data):
        feat = compute_feature_vector(data, i)
        lab = compute_label(data[i], gt, alpha)
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
