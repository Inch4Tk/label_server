from annotation_predictor.GroundTruthReader import GroundTruthReader
from annotation_predictor.test.conftest import test_data, test_file

def test_get_groundtruth_annotation_finds_annotation_for_image():
    with GroundTruthReader(test_file) as test_ground_truth_reader:
        ret = test_ground_truth_reader.get_ground_truth_annotation('test_id')
    assert ret == test_data
