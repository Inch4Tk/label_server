from collections.__init__ import OrderedDict

import numpy as np
from PIL import Image

from annotation_predictor.util.class_reader import ClassReader
from settings import known_class_ids_annotation_predictor

def compute_feature_vector(detections: list, position: int) -> list:
    """
    Compute a feature vector for a detection with the following features:
    (compare https://arxiv.org/abs/1712.08087):
    - score: score of the detection (i.e.: certainty of the object-detector)
    - rel_size: ratio of size of the bounding box of the detection over size of the image
    - avg: average score of all detections on the image
    - avg-dif: difference of score (first feature) and avg (third feature)
    - max_dif: difference of highest score of the image and score (first feature)
    - one_hot_encoding: vector with one entry for each class contained in a dataset which has a one
    for the class of the current detections and zeros everywhere else, uniquely defining the class.
    Args:
        detections: complete detection data for one image
        position: position of the detection for which the feature vector will be computed

    Returns: feature vector with the above features
    """
    class_reader = ClassReader(known_class_ids_annotation_predictor)
    detection = detections[position]
    score = float(detection['Confidence'])
    rel_size = get_rel_size(detection)
    avg = get_avg_score(detections)
    avg_dif = score - avg
    max_dif = get_max_score(detections) - score
    class_index = class_reader.get_index_of_class_from_label(detection['LabelName'])
    # number of classes in oid dataset which is used for base training
    one_hot_encoding = np.zeros(1000)
    one_hot_encoding[class_index] = 1
    feature_vector = [score, rel_size, avg, avg_dif, max_dif]
    feature_vector.extend(one_hot_encoding)
    return feature_vector

def get_rel_size(detection: OrderedDict) -> float:
    """
    Args:
        detection: detection for which the relative size will be computed.

    Returns: relative size of a bounding box in an image
    """
    return round((float(detection['XMax']) - float(detection['XMin'])) * (
            float(detection['YMax']) - float(detection['YMin'])), 10)

def get_avg_score(detections: list) -> float:
    """
    Args:
        detections: All detections for an image.

    Returns: average score of those detections.
    """
    avg_score = 0
    nr_of_detections = len(detections)
    for i in detections:
        avg_score += float(i['Confidence']) / nr_of_detections
    return avg_score

def get_max_score(detections: list) -> float:
    """
    Args:
        detections: All detections for an image.

    Returns: maximum of all scores of those detections.
    """
    max_score = 0
    for i in detections:
        conf = float(i['Confidence'])
        if conf > max_score:
            max_score = conf
    return max_score

def compute_iou(det_a: dict, det_b: dict) -> float:
    """
    Args:
        det_a: First detection
        det_b: Second detection

    Returns: 'Intersection over Union' of two detections which equals the ratio of the
    intersected area of both detection-bounding-boxes over the union of both.
    """
    bbA = [float(det_a['XMin']), float(det_a['YMin']), float(det_a['XMax']), float(det_a['YMax'])]
    bbB = [float(det_b['XMin']), float(det_b['YMin']), float(det_b['XMax']), float(det_b['YMax'])]

    x_min = max(bbA[0], bbB[0])
    y_min = max(bbA[1], bbB[1])
    x_max = min(bbA[2], bbB[2])
    y_max = min(bbA[3], bbB[3])

    intersection_area = max(0.0, x_max - x_min) * max(0.0, y_max - y_min)

    a_area = (bbA[0] - bbA[2]) * (bbA[1] - bbA[3])
    b_area = (bbB[0] - bbB[2]) * (bbB[1] - bbB[3])

    iou = round(intersection_area / float(a_area + b_area - intersection_area), 5)

    return iou

def evaluate_prediction_record(pred: np.ndarray, label: np.ndarray):
    """
    Evaluates the performance of an acceptance-predictor created by accept_prob_predictor.py
    Args:
        pred: Array of acceptance-predictions for a set of images
        label: Ground-truth data for those predictions.

    Returns:
        acc: percentage of correct predictions
        acc_ann: percentage of correct predictions with label 0
        acc_ver: percentage of correct predictions with label 1
    """
    correct = 0
    correct_ver = 0
    correct_ann = 0
    nr_ann = 0
    nr_ver = 0

    for i, prediction in enumerate(pred):
        if label[i] == 1:
            nr_ver += 1
            if prediction > 0.5:
                correct += 1
                correct_ver += 1

        else:
            nr_ann += 1
            if prediction < 0.5:
                correct += 1
                correct_ann += 1

    acc = round(correct / len(pred), 5)

    if nr_ann == 0:
        acc_ann = 0
    else:
        acc_ann = round(correct_ann / nr_ann, 5)

    if nr_ver == 0:
        acc_ver = 0
    else:
        acc_ver = round(correct_ver / nr_ver, 5)

    return acc, acc_ann, acc_ver

def compute_label(detection: OrderedDict, ground_truth: list, alpha: float) -> float:
    """
    Args:
        detection: object-detection on an image
        ground_truth: ground-truth values for this image
        alpha: required value for IoU (Intersection over Union) for the detection
        and a ground-truth value (of the same class)

    Returns: '0' if no ground-truth-box matches the detection, '1' else.
    """
    for i in ground_truth:
        if i['LabelName'] == detection['LabelName'] and compute_iou(i, detection) >= alpha:
            return 1.0
    return 0.0

def load_image(path_to_image: str):
    """
    Args:
        path_to_image: Path to an image-file.

    Returns: Image-data in numpy format which is required for the object-detector.
    """
    img = Image.open(path_to_image).convert('RGB')
    img.load()
    data = np.asarray(img, dtype='uint8')
    data = np.expand_dims(data, 0)

    return data
