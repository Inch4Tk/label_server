from collections import OrderedDict

from annotation_predictor.compute_iou import compute_iou

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