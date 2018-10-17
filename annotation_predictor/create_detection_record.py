import argparse
import json
import os
from datetime import datetime

from PIL import Image

from annotation_predictor.send_od_request import send_od_request
from settings import annotation_predictor_metadata_dir

def create_detection_record(path_to_images: str, path_to_json=None):
    """
    Create and save detections from an object-detection model for a set of images.

    Args:
        path_to_images: Path to a directory which contains the images to be analysed.
        path_to_json: Path to an existent json to which the detections will be appended.
    """
    if path_to_json is None:
        images = os.listdir(path_to_images)
        result = {}
        timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')
        path_to_json = os.path.join(annotation_predictor_metadata_dir, '{}.json'.format(timestamp))
        with open(path_to_json, 'w') as f:
            json.dump(result, f)

    else:
        with open(path_to_json, 'r') as f:
            result = json.load(f)
            images = []
        for image in os.listdir(path_to_images):
            image_id = os.path.splitext(image)[0]
            if image_id not in result.keys():
                images.append(image)

    total_images = len(images)

    for i, image in enumerate(images):
        if (i % 100) == 0:
            with open(path_to_json, 'r+') as f:
                json.dump(result, f)
            print('Evaluated {} of {} images'.format(i, total_images))

        path_to_image = os.path.join(path_to_images, image)
        try:
            Image.open(path_to_image).convert('RGB')
        except (IOError, OSError):
            continue
        result.update(send_od_request(path_to_image))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create and save a detection record for a set of images')
    parser.add_argument('path_to_images', type=str, metavar='path_to_images',
                        help='path to training images')
    parser.add_argument('--path_to_json', type=str, metavar='path_to_json',
                        help='path to exising json file which will be updated', required=False)
    args = parser.parse_args()

    create_detection_record(args.path_to_images, args.path_to_json)
