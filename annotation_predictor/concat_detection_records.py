import argparse
import json
import os
from datetime import datetime

from settings import annotation_predictor_metadata_dir

def concat_detection_record(record1: str, record2: str):
    """
    Concatenates two detection records and saves them in a new file.

    Args:
        record1: Path to first record, saved in a json-file.
        record2: Path to second record, saved in a json-file
    """
    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    filename = '{}.json'.format(timestamp)
    path_to_file = os.path.join(annotation_predictor_metadata_dir, filename)
    with open(record1, 'r') as f:
        r1 = json.load(f)
    with open(record2, 'r') as f:
        r2 = json.load(f)

    r1.update(r2)

    with open(path_to_file, 'w') as f:
        json.dump(r1, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Concatenate two detection records')
    parser.add_argument('path_to_record_1', type=str, metavar='path_to_record_1',
                        help='path to first training record')
    parser.add_argument('path_to_record_2', type=str, metavar='path_to_record_2',
                        help='path to second training record')
    args = parser.parse_args()

    concat_detection_record(args.path_to_record_1, args.path_to_record_2)