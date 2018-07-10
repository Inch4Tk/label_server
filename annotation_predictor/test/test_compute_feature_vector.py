import numpy as np

from annotation_predictor.compute_feature_vector import compute_feature_vector
from annotation_predictor.test.conftest import test_data

def test_compute_feature_vector():
    feature_vector = compute_feature_vector(test_data, 1)
    assert feature_vector[0] == 0.5
    assert feature_vector[1] == 0.01
    assert feature_vector[2] == 0.3
    assert feature_vector[3] == 0.2
    assert feature_vector[4] == 0
#
    one_hot_enc = np.zeros(601)
    one_hot_enc[459] = 1
    assert (feature_vector[5] == one_hot_enc).all
