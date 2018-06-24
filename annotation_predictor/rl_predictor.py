from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Imports
import os

import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)


def rl_model(features, mode):

    # Input Layer:
    x = tf.reshape(features["x"], [-1, 606])

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

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=output)

    if mode == tf.estimator.ModeKeys.TRAIN:
        # TODO Calculate Reward
        reward_holder = tf.placeholder(shape=[1], dtype=tf.float32)
        loss = -reward_holder
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
        train_op = optimizer.minimize(loss=loss)
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)


if __name__ == '__main__':
    # TODO Load training data
    train_data = 0

    rl_predictor = tf.estimator.Estimator(model_fn=rl_model, model_dir=os.path.join(os.getcwd(), 'models'))

    # Train the model
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": train_data},
        batch_size=64,
        shuffle=True)
    rl_predictor.train(
        input_fn=train_input_fn,
        steps=1000,
    )
