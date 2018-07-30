import os
import sys

import numpy as np
import tensorflow as tf
from PIL import Image
from grpc.beta import implementations
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

from annotation_predictor.class_reader import ClassReader
from annotation_predictor.settings import class_ids_coco_file

def load_image(path_to_image: str):
    img = Image.open(path_to_image).convert('RGB')
    img.load()
    data = np.asarray(img, dtype='uint8')
    data = np.expand_dims(data, 0)

    return data

def send_od_request(path_to_image: str):
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

    class_reader = ClassReader(class_ids_coco_file)
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
