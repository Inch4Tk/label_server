import os
from collections import OrderedDict

import pytest

from annotation_predictor.GroundTruthReader import GroundTruthReader
from settings import annotation_predictor_dir

test_file = os.path.join(annotation_predictor_dir, 'test', 'testfiles', 'test.csv')
test_ground_truth_reader = GroundTruthReader(test_file)

test_data = [
    OrderedDict(
        [('ImageID', 'test_id'), ('Source', 'freeform'), ('LabelName', '/m/04242'), ('Confidence', '0.1'),
         ('XMin', '0.1'), ('XMax', '0.2'), ('YMin', '0.3'), ('YMax', '0.4'), ('IsOccluded', '0'), ('IsTruncated', '0'),
         ('IsGroupOf', '0'), ('IsDepiction', '0'), ('IsInside', '1')
         ]),
    OrderedDict(
        [('ImageID', 'test_id'), ('Source', 'freeform'), ('LabelName', '/m/0cdn1'), ('Confidence', '0.5'),
         ('XMin', '0.6'), ('XMax', '0.7'), ('YMin', '0.8'), ('YMax', '0.9'), ('IsOccluded', '1'), ('IsTruncated', '0'),
         ('IsGroupOf', '1'), ('IsDepiction', '0'), ('IsInside', '1')
         ])]

def test_get_groundtruth_annotation_finds_annotation_for_image():
    ret = test_ground_truth_reader.get_ground_truth_annotation('test_id')
    assert ret == test_data

def test_get_class_from_id_with_nonexistent_id():
    with pytest.raises(KeyError, message='This ID does not exist'):
        test_ground_truth_reader.get_class_from_id(test_data[0])

def test_get_class_from_id_with_existent_id():
    assert test_ground_truth_reader.get_class_from_id(test_data[1]) == 'Hamburger'
