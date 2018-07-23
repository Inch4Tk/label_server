from collections.__init__ import OrderedDict

import numpy as np

from annotation_predictor.ClassReader import ClassReader
from settings import class_ids_oid_file

def compute_feature_vector(annotation: list, position: int) -> list:
    class_reader = ClassReader(class_ids_oid_file)
    detection = annotation[position]
    score = float(detection['Confidence'])
    rel_size = get_rel_size(detection)
    avg = get_avg_score(annotation)
    avg_dif = score - avg
    max_dif = score - get_max_score(annotation)
    class_index = class_reader.get_index_of_class(detection['LabelName'])
    one_hot_encoding = np.zeros(len(class_reader.class_ids))
    one_hot_encoding[class_index] = 1
    feature_vector = [score, rel_size, avg, avg_dif, max_dif]
    feature_vector.extend(one_hot_encoding)
    return feature_vector

def get_rel_size(detection: OrderedDict) -> float:
    return round((float(detection['XMax']) - float(detection['XMin'])) * (
            float(detection['YMax']) - float(detection['YMin'])), 10)

def get_avg_score(annotation: list) -> float:
    avg_score = 0
    nr_of_detections = len(annotation)
    for i in annotation:
        avg_score += float(i['Confidence']) / nr_of_detections
    return avg_score

def get_max_score(annotation: list) -> float:
    max_score = 0
    for i in annotation:
        conf = float(i['Confidence'])
        if conf > max_score:
            max_score = conf
    return max_score

def compute_iou(det_a: OrderedDict, det_b: OrderedDict) -> float:
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

def evaluate_prediction_record(pred: np.ndarray, label: list):
    correct = 0
    correct_ver = 0
    correct_ann = 0
    nr_ann = 0
    nr_ver = 0
    for i, prediction in enumerate(pred):
        if prediction > 0.5:
            nr_ver += 1
            if label[i] == 1:
                correct += 1
                correct_ver += 1

        else:
            nr_ann += 1
            if label[i] == 0:
                correct += 1
                correct_ann += 1

    print('Accuracy:\t{} ({} of {})'.format(round(correct / len(pred), 5),
                                            correct, len(pred)))
    print('Accuracy Ann:\t{} ({} of {})'.format(round(correct_ann / nr_ann, 5),
                                                correct_ann, nr_ann))
    if nr_ver == 0:
        print('Accuracy Ver:\t{} ({} of {})'.format(0, correct_ver, nr_ver))
    else:
        print('Accuracy Ver:\t{} ({} of {})'.format(round(correct_ver / nr_ver, 5),
                                                    correct_ver, nr_ver))

def compute_label(detection: OrderedDict, ground_truth: list, alpha: float) -> float:
    for i in ground_truth:
        if i['LabelName'] == detection['LabelName'] and compute_iou(i, detection) >= alpha:
            return 1.0
    return 0.0
