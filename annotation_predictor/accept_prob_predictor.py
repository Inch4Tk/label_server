import argparse
import json
import os
from collections import OrderedDict

import tensorflow as tf

from annotation_predictor.ClassReader import ClassReader
from annotation_predictor.GroundTruthReader import GroundTruthReader
from annotation_predictor.compute_feature_vector import compute_feature_vector
from annotation_predictor.compute_iou import compute_iou
from settings import class_ids_oid_file

tf.logging.set_verbosity(tf.logging.INFO)

def prob_model(features, labels, mode):
    # Input Layer:
    features = tf.constant(features)
    labels = tf.constant(labels)
    zero_padding = tf.zeros(1000 - len(ClassReader(class_ids_oid_file).class_ids))
    x = tf.concat([features, zero_padding], 0)

    # Fully-connected Layer #1
    dense1 = tf.layers.dense(
        inputs=x,
        units=30,
        activation=tf.nn.relu
    )

    # Fully-connected Layer #2
    output = tf.layers.dense(
        inputs=dense1,
        units=1,
        activation=tf.nn.relu
    )

    result = tf.round(tf.nn.softmax(output))

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=output)

    if mode == tf.estimator.ModeKeys.TRAIN:
        for i in range(output):
            reward_holder = tf.placeholder(shape=[1], dtype=tf.float32)
            loss = -reward_holder
            optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
            train_op = optimizer.minimize(loss=loss)
            return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

def compute_label(detection: OrderedDict, ground_truth: list, alpha: float) -> int:
    for i in ground_truth:
        if i['LabelName'] == detection['LabelName'] and compute_iou(i, detection) >= alpha:
            return 1
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a proposal network for labeling tasks')
    parser.add_argument('path_to_detections', type=str, metavar='path_to_detections', help='path to detection data')
    parser.add_argument('path_to_gt', type=str, metavar='path_to_gt', help='path to ground truth data')
    parser.add_argument('--iterations', type=int, help='number of training iterations', default=1000)
    parser.add_argument('--alpha', type=float, help='minimal value of iou for labels', default=0.5)
    args = parser.parse_args()
    iterations = 0
    gt_reader = GroundTruthReader(args.path_to_gt)

    feature_data = []
    label_data = []

    with open(args.path_to_detections) as file:
        detections = json.load(file)

    for key in detections:
        feature = []
        label = []
        gt = gt_reader.get_ground_truth_annotation(key)
        for i, _ in enumerate(detections):
            feature.append(compute_feature_vector(detections[key], i))
            label.append(compute_label(detections[key][i], gt, args.alpha))
        feature_data.append(feature)
        label_data.append(label)

    dataset = tf.data.Dataset.from_tensor_slices((
        {'features': feature_data, 'labels': label_data}))
    dataset.shuffle(buffer_size=len(detections))
    prob_predictor = tf.estimator.Estimator(model_fn=prob_model, model_dir=os.path.join(os.getcwd(), 'models'))

    prob_predictor.train(
        input_fn=dataset,
        steps=args.iterations,
    )
