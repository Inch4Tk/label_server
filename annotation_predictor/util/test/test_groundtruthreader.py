from annotation_predictor.util.groundtruth_reader import GroundTruthReader
from annotation_predictor.util.test.conftest import test_data, test_file, test_dict

def test_get_groundtruth_annotation_finds_annotation_for_image():
    with GroundTruthReader(test_file) as test_ground_truth_reader:
        ret = test_ground_truth_reader.get_ground_truth_annotation('test_id')
    assert ret == test_data

def test_returns_empty_list_for_unknown_id():
    with GroundTruthReader(test_file) as test_ground_truth_reader:
        ret = test_ground_truth_reader.get_ground_truth_annotation('nonexistent')
    assert ret == []

def test_parse_to_dict():
    with GroundTruthReader(test_file) as test_ground_truth_reader:
        assert test_ground_truth_reader.gt_dict == test_dict