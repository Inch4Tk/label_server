import numpy as np
import tensorflow as tf
from grpc.beta import implementations
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

def send_accept_prob_request(feature_vectors: list):
    """
    Get acceptance inference for object detections from a model
    which is available under local port 9000.
    Args:
        feature_vectors: Features of predictions for which the acceptance is inferred.

    Returns: Acceptance inferrence for each prediction

    """
    channel = implementations.insecure_channel('localhost', 9000)

    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    request = predict_pb2.PredictRequest()

    request.model_spec.name = 'prob_predictor'
    request.model_spec.signature_name = 'serving_default'
    request.inputs['inputs'].CopyFrom(tf.make_tensor_proto(feature_vectors, dtype=tf.float32))

    pred_result = stub.Predict(request, 60.0)

    result = np.round(pred_result.outputs['tensorflow/serving/predict'].float_val)
    return result
