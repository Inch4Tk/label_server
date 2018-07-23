import argparse
import json
import os
import random
import sys

import numpy as np
import tensorflow as tf

from annotation_predictor.GroundTruthReader import GroundTruthReader
from annotation_predictor.util import compute_feature_vector, evaluate_prediction_record, \
    compute_label
from settings import model_dir

tf.logging.set_verbosity(tf.logging.INFO)

FLAGS = None

def prob_model(x):
    dense1 = tf.layers.dense(
        inputs=x,
        units=10,
        activation=tf.nn.relu
    )
    dense2 = tf.layers.dense(
        inputs=dense1,
        units=25,
        activation=tf.nn.relu
    )
    dense3 = tf.layers.dense(
        inputs=dense2,
        units=50,
        activation=tf.nn.relu
    )
    dense4 = tf.layers.dense(
        inputs=dense3,
        units=25,
        activation=tf.nn.relu
    )
    dense5 = tf.layers.dense(
        inputs=dense4,
        units=10,
        activation=tf.nn.relu
    )
    y = tf.layers.dense(
        inputs=dense5,
        units=1,
        activation=tf.nn.sigmoid
    )

    return y

def main(_):
    x = tf.placeholder(tf.float32, [None, 606])
    y = prob_model(x)

    saver = tf.train.Saver()

    feature_data = []

    with open(FLAGS.path_to_data) as file:
        detections = json.load(file)

    if FLAGS.mode == 'train':
        label = tf.placeholder(tf.float32, [None, 1])

        batch_size = FLAGS.batch_size
        gt_reader = GroundTruthReader(FLAGS.path_to_gt)

        label_data = []
        feature_data_ones = []

        for key in detections:
            gt = gt_reader.get_ground_truth_annotation(key)
            for i, _ in enumerate(detections[key]):
                feat = compute_feature_vector(detections[key], i)
                lab = compute_label(detections[key][i], gt, FLAGS.alpha)
                feature_data.append(feat)
                label_data.append(lab)
                if lab == 1:
                    feature_data_ones.append(feat)

        zero_offset = label_data.count(0) - label_data.count(1)
        while zero_offset > 0:
            for f in feature_data_ones:
                if zero_offset == 0:
                    break
                feature_data.append(f)
                label_data.append(1.0)
                zero_offset -= 1

        dataset = list(zip(feature_data, label_data))
        random.shuffle(dataset)
        feature_data, label_data = zip(*dataset)

        with open(FLAGS.path_to_test_data) as file:
            test_data = json.load(file)

        test_x = []
        test_label = []

        for key in test_data:
            gt = gt_reader.get_ground_truth_annotation(key)
            for i, _ in enumerate(test_data[key]):
                test_x.append(compute_feature_vector(test_data[key], i))
                test_label.append(compute_label(test_data[key][i], gt, FLAGS.alpha))

        loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=y, labels=label))
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.03)
        train_op = optimizer.minimize(loss=loss, global_step=tf.train.get_global_step())

        correct_prediction = tf.equal(tf.round(y), label)
        correct_prediction = tf.cast(correct_prediction, tf.float32)
        accuracy = tf.reduce_mean(correct_prediction)

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            for i in range(FLAGS.iterations):
                a = i * batch_size
                b = a + batch_size
                if i % 100 == 0:
                    train_accuracy = accuracy.eval(feed_dict={
                        x: np.reshape(feature_data[a:b], (-1, 606)),
                        label: np.reshape(label_data[a:b], (-1, 1))})
                    print('step {},\t training accuracy {}'.format(i, train_accuracy))
                train_op.run(feed_dict={x: np.reshape(feature_data[a:b], (-1, 606)),
                                        label: np.reshape(label_data[a:b], (-1, 1))})

            evaluate_prediction_record(y.eval(feed_dict={
                x: np.reshape(test_x, (-1, 606)), label: np.reshape(test_label, (-1, 1))}).reshape(
                -1),
                test_label)

            saver.save(sess, os.path.join(model_dir, 'prob_predictor.ckpt'))

    elif FLAGS.mode == 'predict':
        for key in detections:
            for i, _ in enumerate(detections[key]):
                feature_data.append(compute_feature_vector(detections[key], i))

        with tf.Session() as sess:
            saver.restore(sess, os.path.join(model_dir, 'prob_predictor.ckpt'))

            sess.run(tf.global_variables_initializer())
            result = y.eval(feed_dict={
                x: np.reshape(feature_data, (-1, 606))})

            prediction = tf.round(result).eval()

            for i, val in enumerate(prediction):
                print('{}: {}'.format(i, val))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a proposal network for labeling tasks')
    parser.add_argument('--mode', type=str, choices=['train', 'predict'],
                        help='define if you want to train the model or use it to predict',
                        required=True)
    parser.add_argument('--path_to_data', type=str,
                        help='path to train/prediction data', required=True)
    parser.add_argument('--path_to_test_data', type=str,
                        help='path to test data', required=False)
    parser.add_argument('--path_to_gt', type=str,
                        help='path to ground truth data', required=False)
    parser.add_argument('--iterations', type=int,
                        help='number of training iterations (relevant for training only)',
                        default=1000)
    parser.add_argument('--batch_size', type=int,
                        help='size of batches send to model',
                        default=64)
    parser.add_argument('--alpha', type=float,
                        help='minimal value of iou for accepting a label (for training only)',
                        default=0.5)
    FLAGS, unparsed = parser.parse_known_args()
    if FLAGS.mode == 'train' and (FLAGS.path_to_test_data is None or FLAGS.path_to_gt is None):
        parser.error(
            'train mode requires the following additional arguments: path_to_test_data, path_to_gt')
    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
