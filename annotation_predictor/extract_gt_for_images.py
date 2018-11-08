import argparse
import json
import os
from datetime import datetime

from annotation_predictor.util.groundtruth_reader import GroundTruthReader
from settings import annotation_predictor_metadata_dir

evaluation_record = {}

def extract_gt(path_to_images: str, path_to_gt: str):
    """
    Extracts ground truth data for a given set of images and saves it in a json-file

    Args:
        path_to_images: test images
        path_to_gt: Ground-Truth-Data which contains data for images as a subset
    """

    gt_json = {}
    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')

    gt_reader = GroundTruthReader(path_to_gt)

    for image in os.listdir(path_to_images):
        image_id = os.path.splitext(image)[0]
        ground_truth = gt_reader.get_ground_truth_annotation(image_id)
        gt_json[image_id] = ground_truth

    with open(os.path.join(annotation_predictor_metadata_dir, timestamp + '.json'), 'w') as f:
        json.dump(gt_json, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Concatenate two detection records')
    parser.add_argument('path_to_gt', type=str, metavar='path_to_gt',
                        help='path to groundtruth')
    parser.add_argument('path_to_images', type=str, metavar='path_to_images',
                        help='path to images')
    args = parser.parse_args()

    extract_gt(args.path_to_images, args.path_to_gt)
