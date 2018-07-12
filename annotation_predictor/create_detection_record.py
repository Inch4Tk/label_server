import argparse
import json
import os
from datetime import datetime

from annotation_predictor.send_od_request import send_od_request
from settings import annotation_predictor_metadata_dir

def create_detection_record(path_to_images: str):
    result = {}
    for image in os.listdir(path_to_images):
        path_to_image = os.path.join(path_to_images, image)
        result.update(send_od_request(path_to_image))

    path_to_json = os.path.join(annotation_predictor_metadata_dir,
                                '{}.json'.format(datetime.now().strftime('%Y_%m_%d_%H%M%S')))
    with open(path_to_json, 'w') as f:
        json.dump(result, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create and save a detection record for a set of images')
    parser.add_argument('path_to_images', type=str, metavar='path_to_images', help='path to training images')
    args = parser.parse_args()

    create_detection_record(args.path_to_images)
