import argparse
import os
import sys

import numpy as np
import tensorflow as tf
from tensorflow.python.framework.errors_impl import OutOfRangeError
from tensorflow.python.saved_model import tag_constants

from annotation_predictor.util.settings import model_dir
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
        activation=tf.nn.sigmoid
    )

    return y

def main(mode: str, detections=None):
    """
    Trains a model or uses an existent model to make predictions.

    Args:
        mode: Defines whether a model should be trained
        or an existent model should be used for making predictions.
        detections: Used in detection-mode to give a list of detections
        for which predictions should be generated.
    """
    x = tf.placeholder(tf.float32, [None, 606])
    y = prob_model(x)

    saver = tf.train.Saver()

    accept_prob_model_dir = os.path.join(model_dir, 'accept_prob_predictor')

    if not os.path.exists(accept_prob_model_dir):
        os.mkdir(accept_prob_model_dir)

    existent_checkpoints = os.listdir(accept_prob_model_dir)
    actual_checkpoint = len(existent_checkpoints)
    new_checkpoint = str(actual_checkpoint + 1)
    actual_checkpoint = str(actual_checkpoint)
    actual_checkpoint_dir = os.path.join(model_dir, 'accept_prob_predictor', actual_checkpoint)
    new_checkpoint_dir = os.path.join(model_dir, 'accept_prob_predictor', new_checkpoint)

    if FLAGS and FLAGS.mode == 'train':
        _y = tf.placeholder(tf.float32, [None, 1])

        best_acc = 0.0
        best_acc_ann = 0.0
        best_acc_ver = 0.0
        early_stopping_counter = 0

        builder = tf.saved_model.builder.SavedModelBuilder(new_checkpoint_dir)

        loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=y, labels=_y))
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=FLAGS.learning_rate)
        train_op = optimizer.minimize(loss=loss, global_step=tf.train.get_global_step())

        with tf.Session() as sess:
            base = FLAGS.path_to_training_data
            path_to_train_data = '{}_{}'.format(base, 'train.tfrecords')
            path_to_test_data = '{}_{}'.format(base, 'test.tfrecords')

            train_datapoint = {'train/feature': tf.FixedLenFeature([606], tf.float32),
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

            test_feat = []
            test_lbl = []
            example = tf.train.Example()
            for record in tf.python_io.tf_record_iterator(path_to_test_data):
                example.ParseFromString(record)
                f = example.features.feature
                test_feat.append(np.asarray(f['test/feature'].float_list.value))
                test_lbl.append(f['test/label'].float_list.value[0])
            test_feat = np.reshape(test_feat, (-1, 606))
            test_lbl = np.reshape(test_lbl, (-1, 1))

            init_op = tf.group(tf.global_variables_initializer(),
                               tf.local_variables_initializer())
            sess.run(init_op)

            if new_checkpoint != '1':
                saver.restore(sess, os.path.join(accept_prob_model_dir, actual_checkpoint,
                                                 'prob_predictor.ckpt'))

            prediction_input = tf.saved_model.utils.build_tensor_info(x)
            prediction_output = tf.saved_model.utils.build_tensor_info(y)
            prediction_signature = (
                tf.saved_model.signature_def_utils.build_signature_def(
                    inputs={tf.saved_model.signature_constants.PREDICT_INPUTS: prediction_input},
                    outputs={
                        tf.saved_model.signature_constants.PREDICT_METHOD_NAME: prediction_output},
                    method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME)
            )
            legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')

            builder.add_meta_graph_and_variables(
                sess,
                [tag_constants.SERVING],
                signature_def_map={'predict_accept_prob': prediction_signature},
                legacy_init_op=legacy_init_op)

            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(coord=coord)

            for batch_index in range(FLAGS.iterations):
                try:
                    feat, lbl = sess.run([train_features, train_labels])
                except OutOfRangeError:
                    print('No more Training Data available')
                    break

                if batch_index % 100 == 0:
                    y_test = y.eval(feed_dict={x: test_feat, _y: test_lbl})
                    acc, acc_ann, acc_ver = evaluate_prediction_record(y_test, test_lbl)
                    print('step {},\t Annotation acc.:{}\tVerification acc.:{}'.format(batch_index,
                                                                                       acc_ann,
                                                                                       acc_ver))
                    if acc_ann + acc_ver > best_acc_ann + best_acc_ver:
                        best_acc = acc
                        best_acc_ann = acc_ann
                        best_acc_ver = acc_ver
                        early_stopping_counter = 0
                        saver.save(sess, os.path.join(new_checkpoint_dir, 'prob_predictor.ckpt'))
                        builder.save()

                    elif early_stopping_counter == 50:
                        print('Stopped early at batch {}/{}'.format(batch_index, FLAGS.iterations))
                        break
                    else:
                        early_stopping_counter += 1

                train_op.run(feed_dict={x: feat,
                                        _y: lbl})

            print('Accuracy:\t{}'.format(best_acc))
            print('Accuracy Ann:\t{}'.format(best_acc_ann))
            print('Accuracy Ver:\t{}'.format(best_acc_ver))

            # Stop the threads
            coord.request_stop()

            # Wait for threads to stop
            coord.join(threads)
            sess.close()

    elif mode == 'predict':
        feature_data = []

        for key in detections:
            for i, _ in enumerate(detections[key]):
                feature_data.append(compute_feature_vector(detections[key], i))

        with tf.Session() as sess:
            saver.restore(sess, os.path.join(actual_checkpoint_dir, 'prob_predictor.ckpt'))

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
                        help='timestamp of set of tf_record-files in metadata',
                        required=False)
    parser.add_argument('--iterations', type=int,
                        help='number of training iterations (relevant for training only)',
                        default=1000)
    parser.add_argument('--batch_size', type=int,
                        help='size of batches send to model',
                        default=64)
    parser.add_argument('--learning_rate', type=float,
                        help='learning rate (hyperparameter for training)',
                        default=0.03)
    FLAGS, unparsed = parser.parse_known_args()
    args = parser.parse_args()

    if FLAGS.mode == 'train' and (FLAGS.path_to_training_data is None):
        parser.error('train mode requires path_to_training_data')
    if FLAGS.mode == 'predict' and (FLAGS.path_to_prediction_data is None):
        parser.error('predict mode requires path to data')

    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
