import argparse
import json
import os
from collections import OrderedDict

import numpy as np
import tensorflow as tf

from annotation_predictor.GroundTruthReader import GroundTruthReader
from annotation_predictor.util import compute_feature_vector, compute_iou

tf.logging.set_verbosity(tf.logging.INFO)

def prob_model(features, labels, mode):
    dense1 = tf.layers.dense(
        inputs=features['x'],
        units=5,
        activation=tf.nn.relu
    )
    dense2 = tf.layers.dense(
        inputs=dense1,
        units=30,
        activation=tf.nn.relu
    )
    dense3 = tf.layers.dense(
        inputs=dense2,
        units=30,
        activation=tf.nn.relu
    )
    dense4 = tf.layers.dense(
        inputs=dense3,
        units=5,
        activation=tf.nn.relu
    )

    output = tf.layers.dense(
        inputs=dense4,
        units=1,
        activation=tf.nn.relu
    )
    prediction = tf.sigmoid(output)

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=prediction)
    loss = tf.reduce_mean(tf.keras.backend.binary_crossentropy(target=labels, output=output))
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
    train_op = optimizer.minimize(loss=loss, global_step=tf.train.get_global_step())

    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

def compute_label(detection: OrderedDict, ground_truth: list, alpha: float) -> float:
    for i in ground_truth:
        if i['LabelName'] == detection['LabelName'] and compute_iou(i, detection) >= alpha:
            return 1.0
    return 0.0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a proposal network for labeling tasks')
    parser.add_argument('path_to_data', type=str, metavar='path_to_data',
                        help='path to train/test/prediction data')
    parser.add_argument('path_to_gt', type=str, metavar='path_to_gt',
                        help='path to ground truth data')
    parser.add_argument('mode', type=str, metavar='mode', choices=['train', 'eval', 'predict'],
                        help='define if you want to train, evaluate or use the model to predict')
    parser.add_argument('--iterations', type=int,
                        help='number of training iterations (relevant for training only)',
                        default=1000)
    parser.add_argument('--alpha', type=float,
                        help='minimal value of iou for accepting a label (for training only)',
                        default=0.5)
    args = parser.parse_args()

    gt_reader = GroundTruthReader(args.path_to_gt)
    prob_predictor = tf.estimator.Estimator(model_fn=prob_model,
                                            model_dir=os.path.join(os.getcwd(), 'models'))
    with open(args.path_to_data) as file:
        detections = json.load(file)
    feature_data = []
    label_data = []

    for key in detections:
        gt = gt_reader.get_ground_truth_annotation(key)
        for i, _ in enumerate(detections[key]):
            feature_data.append(compute_feature_vector(detections[key], i))
            label_data.append(compute_label(detections[key][i], gt, args.alpha))

    input_fn = tf.estimator.inputs.numpy_input_fn(
        x={'x': np.array(feature_data)},
        y=np.reshape(np.array(label_data), (-1, 1)),
        shuffle=True,
        batch_size=64)

    if args.mode == 'train':
        prob_predictor.train(input_fn=input_fn, steps=args.iterations)

    elif args.mode == 'eval':
        prob_predictor.evaluate(input_fn=input_fn)

    elif args.mode == 'predict':
        predictions = list(prob_predictor.predict(input_fn=input_fn))
        for prediction in predictions:
            print(prediction)
