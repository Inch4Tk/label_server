import os
from collections import OrderedDict

from annotation_predictor.util.class_reader import ClassReader
from annotation_predictor.util.groundtruth_reader import GroundTruthReader
from annotation_predictor.util.settings import known_class_ids_annotation_predictor, \
    annotation_predictor_util_dir

test_file = os.path.join(annotation_predictor_util_dir, 'test', 'testfiles', 'test.csv')
test_ground_truth_reader = GroundTruthReader(test_file)
test_classreader = ClassReader(known_class_ids_annotation_predictor)

test_data = [
    OrderedDict(
        [('Source', 'freeform'), ('LabelName', '/m/04242'), ('Confidence', '0.1'),
         ('XMin', '0.1'), ('XMax', '0.2'), ('YMin', '0.3'), ('YMax', '0.4'), ('IsOccluded', '0'),
         ('IsTruncated', '0'),
         ('IsGroupOf', '0'), ('IsDepiction', '0'), ('IsInside', '1')
         ]),
    OrderedDict(
        [('Source', 'freeform'), ('LabelName', '/m/0cdn1'), ('Confidence', '0.5'),
         ('XMin', '0.6'), ('XMax', '0.7'), ('YMin', '0.8'), ('YMax', '0.9'), ('IsOccluded', '1'),
         ('IsTruncated', '0'),
         ('IsGroupOf', '1'), ('IsDepiction', '0'), ('IsInside', '1')
         ])]

test_dict = {
    'nottest_id': [OrderedDict(
        [('Source', 'freeform'), ('LabelName', '/m/05656'), ('Confidence', '0.8'), ('XMin', '0.5'),
         ('XMax', '0.3'),
         ('YMin', '0.9'), ('YMax', '0.7'), ('IsOccluded', '0'), ('IsTruncated', '1'),
         ('IsGroupOf', '0'),
         ('IsDepiction', '0'), ('IsInside', '1')])],
    'test_id': test_data,
    'test_id_fake': [OrderedDict(
        [('Source', 'freeform'), ('LabelName', '/m/01234'), ('Confidence', '0.1'), ('XMin', '0.8'),
         ('XMax', '0.4'),
         ('YMin', '0.3'), ('YMax', '0.4'), ('IsOccluded', '0'), ('IsTruncated', '0'),
         ('IsGroupOf', '1'),
         ('IsDepiction', '0'), ('IsInside', '1')])]}
