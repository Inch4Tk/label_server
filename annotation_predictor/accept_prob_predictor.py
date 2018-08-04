import argparse
import json
import os
import random
import sys

import numpy as np
import tensorflow as tf

from annotation_predictor.util.settings import model_dir
from annotation_predictor.util.util import compute_feature_vector, evaluate_prediction_record

tf.logging.set_verbosity(tf.logging.INFO)

FLAGS = None

def prob_model(x):
    """ Defines the structure and computations of the neural network."""
    dense1 = tf.layers.dense(
        inputs=x,
        units=50,
        activation=tf.nn.relu
    )
    dense2 = tf.layers.dense(
        inputs=dense1,
        units=25,
        activation=tf.nn.relu
    )
    dense3 = tf.layers.dense(
        inputs=dense2,
        units=20,
        activation=tf.nn.relu
    )
    dense4 = tf.layers.dense(
        inputs=dense3,
        units=15,
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

def main(mode: str, detections=None):
    """
    Trains a new model or uses an existent model to make predictions.

    Args:
        mode: Defines whether a new model should be trained
        or an existent model should be used for making predictions.
        detections: Used in detection-mode to give a list of detections
        for which predictions should be generated.
    """
    x = tf.placeholder(tf.float32, [None, 606])
    y = prob_model(x)

    saver = tf.train.Saver()

    if FLAGS and FLAGS.mode == 'train':
        label = tf.placeholder(tf.float32, [None, 1])

        batch_size = FLAGS.batch_size
        base = FLAGS.path_to_training_data
        path_to_feature_data_train = '{}_{}'.format(base, 'features_train.txt')
        path_to_label_data_train = '{}_{}'.format(base, 'labels_train.txt')
        path_to_feature_data_test = '{}_{}'.format(base, 'features_test.txt')
        path_to_label_data_test = '{}_{}'.format(base, 'labels_test.txt')

        with open(path_to_feature_data_train, 'r') as f:
            feature_data_train = json.load(f)
        with open(path_to_label_data_train, 'r') as f:
            label_data_train = json.load(f)
        with open(path_to_feature_data_test, 'r') as f:
            feature_data_test = json.load(f)
        with open(path_to_label_data_test, 'r') as f:
            label_data_test = json.load(f)

        dataset = list(zip(feature_data_train, label_data_train))
        random.shuffle(dataset)
        feature_data, label_data = zip(*dataset)

        loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=y, labels=label))
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=FLAGS.learning_rate)
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
                x: np.reshape(feature_data_test, (-1, 606)),
                label: np.reshape(label_data_test, (-1, 1))}).reshape(-1),
                                       label_data_test)

            saver.save(sess, os.path.join(model_dir, 'prob_predictor.ckpt'))

    elif mode == 'predict':
        feature_data = []

        for key in detections:
            for i, _ in enumerate(detections[key]):
                feature_data.append(compute_feature_vector(detections[key], i))

        with tf.Session() as sess:
            saver.restore(sess, os.path.join(model_dir, 'prob_predictor.ckpt'))

            result = y.eval(feed_dict={
                x: np.reshape(feature_data, (-1, 606))})
            prediction = tf.round(result).eval()

        for i, val in enumerate(prediction):
            print('{}: {}'.format(i, val))
        return prediction

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a proposal network for labeling tasks')
    parser.add_argument('--mode', type=str, choices=['train', 'predict'],
                        help='define if you want to train the model or use it to predict',
                        required=True)
    parser.add_argument('--path_to_prediction_data', type=str,
                        help='path to prediction data', required=False)
    parser.add_argument('--path_to_training_data', type=str,
                        help='train data (filename without "(features/labels)_(train/test).txt")',
                        required=False)
    parser.add_argument('--iterations', type=int,
                        help='number of training iterations (relevant for training only)',
                        default=1000)
    parser.add_argument('--batch_size', type=int,
                        help='size of batches send to model',
                        default=64)
    parser.add_argument('--learning_rate', type=float,
                        help='learning rate (hyperparameter for training)',
                        default=0.04)
    FLAGS, unparsed = parser.parse_known_args()
    args = parser.parse_args()

    if FLAGS.mode == 'train' and (FLAGS.path_to_training_data is None):
        parser.error('train mode requires path_to_training_data')
    if FLAGS.mode == 'predict' and (FLAGS.path_to_prediction_data is None):
        parser.error('train mode requires path to data')

    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
