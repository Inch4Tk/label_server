import argparse
import json
import os

from PIL import Image, ImageDraw

def visualize_detection(path_to_image: str, detection: list):
    img = Image.open(path_to_image)
    colors = ['blue', 'green', 'red', 'orange', 'brown']
    width, height = img.size
    draw = ImageDraw.Draw(img)
    for i, det in enumerate(detection):
        x_min = det['XMin'] * height
        y_min = det['YMin'] * width
        x_max = det['XMax'] * height
        y_max = det['YMax'] * width
        draw.text((x_min, y_min), det['LabelName'])
        for offset in [-1, 0, 1]:
            draw.rectangle(xy=[x_min + offset, y_min + offset, x_max + offset, y_max + offset],
                           outline=colors[i % len(colors)])
    img.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a proposal network for labeling tasks')
    parser.add_argument('path_to_image', type=str, metavar='path_to_image', help='path to image')
    parser.add_argument('path_to_detection', type=str, metavar='path_to_detection',
                        help='path to detection data')

    args = parser.parse_args()
    with open(args.path_to_detection) as f:
        detection = json.load(f)
    image_id = os.path.splitext(os.path.basename(args.path_to_image))[0]
    visualize_detection(args.path_to_image, detection[image_id])
