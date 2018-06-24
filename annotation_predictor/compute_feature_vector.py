import numpy as np

def compute_feature_vector(annotation: dict):
    score = 0
    rel_size = 0
    avg_score = 0
    avg_dif = 0
    max_dif = 0
    one_hot_encoding = np.zeros(601)