from collections import OrderedDict

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
