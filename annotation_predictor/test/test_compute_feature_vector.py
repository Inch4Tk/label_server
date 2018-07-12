import numpy as np

from annotation_predictor.compute_feature_vector import compute_feature_vector
from annotation_predictor.test.conftest import test_data

def test_compute_feature_vector():
    feature_vector = compute_feature_vector(test_data, 1)
    expected = [0.5, 0.01, 0.3, 0.2, 0.0]
    expected_one_hot_enc = np.zeros(601)
    expected_one_hot_enc[459] = 1
    expected.extend(expected_one_hot_enc)
    assert feature_vector == expected
