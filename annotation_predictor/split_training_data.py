import argparse
import json
import os
import random

def split_training_data(data_path: str, ratio: float):
    with open(data_path) as file:
        data = json.load(file)
    keys = list(data.keys())
    random.shuffle(keys)
    test_data = {}

    for i, key in enumerate(keys):
        if i > (len(keys) * ratio):
            break
        test_data.update({key: data[key]})
        data.pop(key)
    basename = os.path.splitext(os.path.basename(data_path))[0]
    base = os.path.join(os.path.dirname(data_path), basename)
    path_to_test_data = '{}_{}'.format(base, 'test.json')
    path_to_training_data = '{}_{}'.format(base, 'training.json')
    with open(path_to_test_data, 'w') as f:
        json.dump(test_data, f)
    with open(path_to_training_data, 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Split a detection record in training and test data')
    parser.add_argument('path_to_detections', type=str, metavar='path_to_detections',
                        help='path to detection data')
    parser.add_argument('--ratio', type=float, help='ratio of test vs. training data', default=0.2)
    args = parser.parse_args()

    split_training_data(args.path_to_detections, args.ratio)
