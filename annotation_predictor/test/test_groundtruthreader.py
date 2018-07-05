import os
from collections import OrderedDict

from annotation_predictor.GroundTruthReader import GroundTruthReader
from settings import annotation_predictor_dir

test_file = os.path.join(annotation_predictor_dir, 'test', 'testfiles', 'test.csv')

expected = [
    OrderedDict(
        [('ImageID', 'test_annotation'), ('Source', 'freeform'), ('LabelName', '/m/04242'), ('Confidence', '0.1'),
         ('XMin', '0.1'), ('XMax', '0.2'), ('YMin', '0.3'), ('YMax', '0.4'), ('IsOccluded', '0'), ('IsTruncated', '0'),
         ('IsGroupOf', '0'), ('IsDepiction', '0'), ('IsInside', '1')
         ]),
    OrderedDict(
        [('ImageID', 'test_annotation'), ('Source', 'freeform'), ('LabelName', '/m/01337'), ('Confidence', '0.5'),
         ('XMin', '0.6'), ('XMax', '0.7'), ('YMin', '0.8'), ('YMax', '0.9'), ('IsOccluded', '1'), ('IsTruncated', '0'),
         ('IsGroupOf', '1'), ('IsDepiction', '0'), ('IsInside', '1')
         ])]

def test_get_groundtruth_annotation_finds_annotation_for_image():
    test_ground_truth_reader = GroundTruthReader(test_file)
    ret = test_ground_truth_reader.get_ground_truth_annotation('test_annotation')
    assert ret == expected
