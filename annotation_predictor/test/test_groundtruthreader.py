from annotation_predictor.test.conftest import test_ground_truth_reader, test_data

def test_get_groundtruth_annotation_finds_annotation_for_image():
    ret = test_ground_truth_reader.get_ground_truth_annotation('test_id')
    assert ret == test_data
