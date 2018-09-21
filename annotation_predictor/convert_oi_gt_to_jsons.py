import argparse
import csv
import json
import os
from datetime import datetime

from annotation_predictor.util.settings import annotation_predictor_metadata_dir

def convert(path_to_csv: str):
    """
    Read in a csv-file containing ground-truth data from the OpenImages Dataset and save it in a
    dict
    """
    gt_dicts = [{} for _ in range(16)]
    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')

    gt_file = open(path_to_csv)
    reader = csv.DictReader(gt_file)

    for entry in reader:
        key = entry['ImageID']
        entry.pop('ImageID')
        char0 = int(key[0], 16)
        if key in gt_dicts[char0]:
            gt_dicts[char0][key].append(entry)
        else:
            gt_dicts[char0][key] = [entry]

    for i, dict in enumerate(gt_dicts):
        filename = os.path.join(annotation_predictor_metadata_dir,
                                timestamp + '_gt_' + hex(i)[2] + '.json')
        with open(filename, 'w') as f:
            json.dump(dict, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Read in a csv-file from the OpenImages Dataset '
                    'containing ground-truth data and save it in a dict')
    parser.add_argument('--path_to_csv', type=str, metavar='path_to_csv_file',
                        help='path to detection data', required=True)
    args = parser.parse_args()

    convert(path_to_csv=args.path_to_csv)
