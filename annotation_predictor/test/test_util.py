from collections import OrderedDict

import numpy as np

from annotation_predictor.test.conftest import test_data
from annotation_predictor.util import compute_iou, compute_feature_vector

def test_compute_iou_for_non_overlap():
    box1 = OrderedDict([('XMin', '0.1'), ('XMax', '0.2'), ('YMin', '0.1'), ('YMax', '0.2')])
    box2 = OrderedDict([('XMin', '0.3'), ('XMax', '0.4'), ('YMin', '0.3'), ('YMax', '0.4')])
    result = compute_iou(box1, box2)
    assert result == 0

def test_compute_iou_for_full_overlap():
    box1 = OrderedDict([('XMin', '0.1'), ('XMax', '0.3'), ('YMin', '0.1'), ('YMax', '0.2')])
    box2 = OrderedDict([('XMin', '0.1'), ('XMax', '0.3'), ('YMin', '0.1'), ('YMax', '0.2')])
    result = compute_iou(box1, box2)
    assert result == 1

def test_compute_iou_for_partial_overlap():
    box1 = OrderedDict([('XMin', '0.0'), ('XMax', '1.0'), ('YMin', '0.0'), ('YMax', '1.0')])
    box2 = OrderedDict([('XMin', '0.3'), ('XMax', '0.5'), ('YMin', '0.6'), ('YMax', '0.8')])
    result = compute_iou(box1, box2)
    assert result == 0.04

def test_compute_feature_vector():
    feature_vector = compute_feature_vector(test_data, 1)
    expected = [0.5, 0.01, 0.3, 0.2, 0.0]
    expected_one_hot_enc = np.zeros(601)
    expected_one_hot_enc[459] = 1
    expected.extend(expected_one_hot_enc)
    assert feature_vector == expected