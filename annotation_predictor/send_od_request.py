import os
import sys

import tensorflow as tf
from grpc.beta import implementations
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

from annotation_predictor.util.class_reader import ClassReader
from annotation_predictor.util.settings import path_to_known_class_ids
from annotation_predictor.util.util import load_image

def send_od_request(path_to_image: str):
    """
    Send a detection request to an object-detector which is available under local port 9000.
    Args:
        path_to_image: Path to an image on which object will be detected

    Returns: List of all detections on the given image

    """
    channel = implementations.insecure_channel('localhost', 9000)

    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    request = predict_pb2.PredictRequest()

    request.model_spec.name = 'mobile_v2'
    request.model_spec.signature_name = 'serving_default'

    img = load_image(path_to_image)
    request.inputs['inputs'].CopyFrom(tf.make_tensor_proto(img, dtype=tf.uint8))

    pred_result = stub.Predict(request, 60.0)
    bounding_boxes = pred_result.outputs['detection_boxes'].float_val
    classes = pred_result.outputs['detection_classes'].float_val
    scores = pred_result.outputs['detection_scores'].float_val

    filename = os.path.basename(path_to_image)
    image_id = os.path.splitext(filename)[0]

    result = {image_id: []}

    class_reader = ClassReader(path_to_known_class_ids)
    for i, cls in enumerate(classes):
        confidence = scores[i]

        if confidence == 0.0:
            break

        label_name = class_reader.get_class_from_id(str(cls))
        ymin = bounding_boxes[4 * i]
        xmin = bounding_boxes[4 * i + 1]
        ymax = bounding_boxes[4 * i + 2]
        xmax = bounding_boxes[4 * i + 3]
        result[image_id].append({'LabelName': label_name, 'Confidence': confidence,
                                 'XMin': xmin, 'YMin': ymin, 'XMax': xmax, 'YMax': ymax})
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(-1)
    result = send_od_request(sys.argv[1])
    print(result)
