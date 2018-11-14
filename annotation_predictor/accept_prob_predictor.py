import argparse
import os
import shutil
import sys

import numpy as np
import tensorflow as tf
from tensorflow.python.framework.errors_impl import OutOfRangeError
from tensorflow.python.saved_model.simple_save import simple_save

from settings import model_dir, path_to_test_data
from annotation_predictor.util.util import compute_feature_vector, evaluate_prediction_record

tf.logging.set_verbosity(tf.logging.INFO)

FLAGS = None

def prob_model(x):
    """ Defines the structure and computations of the neural network."""
    dense1 = tf.layers.dense(
        inputs=x,
        units=150,
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
        activation=tf.nn.sigmoid,
    )

    return y

def parse_tf_records(path_to_train_data):
    train_datapoint = {'train/feature': tf.FixedLenFeature([1005], tf.float32),
                       'train/label': tf.FixedLenFeature([1], tf.float32)}
    train_queue = tf.train.string_input_producer([path_to_train_data], num_epochs=50)
    train_reader = tf.TFRecordReader()
    _, serialized_example = train_reader.read(train_queue)
    train_data = tf.parse_single_example(serialized_example, features=train_datapoint)
    train_feature = tf.cast(train_data['train/feature'], tf.float32)
    train_label = tf.cast(train_data['train/label'], tf.float32)
    train_features, train_labels = tf.train.shuffle_batch([train_feature, train_label],
                                                          batch_size=FLAGS.batch_size,
                                                          capacity=50000,
                                                          min_after_dequeue=0,
                                                          allow_smaller_final_batch=True)
    return train_features, train_labels

def main(mode: str, user_feedback=None, detections=None):
    """
    Trains a model or uses an existent model to make predictions.

    Args:
        mode: Defines whether a model should be trained
        or an existent model should be used for making predictions.
        user_feedback: Used in live-train-mode to train the model based on user input.
        detections: Used in detection-mode to give a list of detections
        for which predictions should be generated.
    """
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.1)

    accept_prob_model_dir = os.path.join(model_dir, 'accept_prob_predictor')

    if not os.path.exists(accept_prob_model_dir):
        os.mkdir(accept_prob_model_dir)

    existent_checkpoints = os.listdir(accept_prob_model_dir)
    existent_checkpoints.sort(key=int)

    x = tf.placeholder(tf.float32, [None, 1005])
    y = prob_model(x)
    _y = tf.placeholder(tf.float32, [None, 1])
    loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=y, labels=_y))

    saver = tf.train.Saver()

    while True:
        actual_checkpoint_dir = ''
        if len(existent_checkpoints) == 0:
            new_checkpoint_dir = os.path.join(accept_prob_model_dir, '1')
            break
        actual_checkpoint = existent_checkpoints[len(existent_checkpoints) - 1]
        actual_checkpoint_dir = os.path.join(accept_prob_model_dir, actual_checkpoint)
        if len(os.listdir(actual_checkpoint_dir)) > 0:
            new_checkpoint_dir = os.path.join(accept_prob_model_dir,
                                              str(int(actual_checkpoint) + 1))
            break

        existent_checkpoints.remove(actual_checkpoint)
        shutil.rmtree(actual_checkpoint_dir)

    if (FLAGS and FLAGS.mode == 'train') or mode == 'train':
        # initial train mode with fixed training data
        if not user_feedback:
            iterations = FLAGS.iterations
            learning_rate = FLAGS.learning_rate
            base = FLAGS.path_to_training_data
            path_to_train_data = '{}_{}'.format(base, 'train.tfrecords')
            train_features, train_labels = parse_tf_records(path_to_train_data)

        # live train mode with user feedback
        else:
            iterations = 1
            learning_rate = 0.001
            batch_size = 64
            train_features, train_labels = tf.train.shuffle_batch([user_feedback['x'],
                                                                   user_feedback['y_']],
                                                                  batch_size=batch_size,
                                                                  capacity=50000,
                                                                  min_after_dequeue=0,
                                                                  allow_smaller_final_batch=True)

        test_feat = []
        test_lbl = []
        example = tf.train.Example()
        for record in tf.python_io.tf_record_iterator(path_to_test_data):
            example.ParseFromString(record)
            f = example.features.feature
            test_feat.append(np.asarray(f['test/feature'].float_list.value))
            test_lbl.append(f['test/label'].float_list.value[0])
        test_feat = np.reshape(test_feat, (-1, 1005))
        test_lbl = np.reshape(test_lbl, (-1, 1))

        init_op = tf.group(tf.global_variables_initializer(),
                           tf.local_variables_initializer())

        optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
        train_op = optimizer.minimize(loss=loss, global_step=tf.train.get_global_step())

        best_acc = 0.0
        best_acc_ann = 0.0
        best_acc_ver = 0.0
        early_stopping_counter = 0

        with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:

            sess.run(init_op)

            if len(existent_checkpoints) > 0:
                saver.restore(sess, os.path.join(actual_checkpoint_dir, 'prob_predictor.ckpt'))

            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(coord=coord)

            for batch_index in range(iterations):
                try:
                    feat, lbl = sess.run([train_features, train_labels])
                except OutOfRangeError:
                    print('No more Training Data available')
                    break

                train_op.run(feed_dict={x: np.reshape(feat, (-1, 1005)),
                                        _y: np.reshape(lbl, (-1, 1))})

                if batch_index % 100 == 0 or user_feedback:
                    y_test = y.eval(feed_dict={x: test_feat, _y: test_lbl})
                    acc, acc_ann, acc_ver = evaluate_prediction_record(y_test, test_lbl)
                    print('step {},\t Annotation acc.:{}\tVerification acc.:{}'.format(batch_index,
                                                                                       acc_ann,
                                                                                       acc_ver))

                    if user_feedback:
                        if os.path.exists(new_checkpoint_dir):
                            shutil.rmtree(new_checkpoint_dir)
                        simple_save(sess,
                                    new_checkpoint_dir,
                                    inputs={'inputs': x},
                                    outputs={'outputs': y})
                        saver.save(sess, os.path.join(new_checkpoint_dir, 'prob_predictor.ckpt'))

                    if acc_ann + acc_ver > best_acc_ann + best_acc_ver:
                        if os.path.exists(new_checkpoint_dir):
                            shutil.rmtree(new_checkpoint_dir)

                        best_acc = acc
                        best_acc_ann = acc_ann
                        best_acc_ver = acc_ver
                        early_stopping_counter = 0
                        simple_save(sess,
                                    new_checkpoint_dir,
                                    inputs={'inputs': x},
                                    outputs={'outputs': y})
                        saver.save(sess, os.path.join(new_checkpoint_dir, 'prob_predictor.ckpt'))
                    # elif early_stopping_counter == 50:
                    #     print('Stopped early at batch {}/{}'.format(batch_index, iterations))
                    #     break
                    else:
                        early_stopping_counter += 1

            print('Accuracy:\t{}'.format(best_acc))
            print('Accuracy Ann:\t{}'.format(best_acc_ann))
            print('Accuracy Ver:\t{}'.format(best_acc_ver))

            # Stop the threads
            coord.request_stop()

            # Wait for threads to stop
            coord.join(threads)
            sess.close()

    elif mode == 'predict' and len(existent_checkpoints) > 0:
        feature_data = []
        for key in detections:
            for i, _ in enumerate(detections[key]):
                feature_data.append(compute_feature_vector(detections[key][i]))

        with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:
            saver.restore(sess, os.path.join(actual_checkpoint_dir, 'prob_predictor.ckpt'))

            result = y.eval(feed_dict={
                x: np.reshape(feature_data, (-1, 1005))})
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
                        help='timestamp of set of tf_record-files in metadata',
                        required=False)
    parser.add_argument('--iterations', type=int,
                        help='number of training iterations (relevant for training only)',
                        default=30000)
    parser.add_argument('--batch_size', type=int,
                        help='size of batches send to model',
                        default=64)
    parser.add_argument('--learning_rate', type=float,
                        help='learning rate (hyperparameter for training)',
                        default=0.05)
    FLAGS, unparsed = parser.parse_known_args()
    args = parser.parse_args()

    if FLAGS.mode == 'train' and (FLAGS.path_to_training_data is None):
        parser.error('train mode requires path_to_training_data')
    if FLAGS.mode == 'predict' and (FLAGS.path_to_prediction_data is None):
        parser.error('predict mode requires path to data')

    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
