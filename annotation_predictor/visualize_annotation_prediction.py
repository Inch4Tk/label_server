import argparse
import os

from PIL import Image, ImageDraw

from annotation_predictor import accept_prob_predictor
from object_detector.send_od_request import send_od_request

def visualize_detection(path_to_image: str):
    """
    Visualizes object-detections and corresponding acceptance probability predictions for an image.
    Args:
        path_to_image: Image on which detections and predictions will be visualized.
    """
    det = send_od_request(path_to_image)
    pred = accept_prob_predictor.main('predict', detections=det)
    image_id = os.path.splitext(os.path.basename(path_to_image))[0]
    img = Image.open(path_to_image)
    colors = ['blue', 'green', 'red', 'orange', 'brown', 'black', 'turquoise']
    width, height = img.size
    draw = ImageDraw.Draw(img)
    for i, det in enumerate(det[image_id]):
        color = colors[i % len(colors)]
        x_min = det['XMin'] * width
        y_min = det['YMin'] * height
        x_max = det['XMax'] * width
        y_max = det['YMax'] * height
        draw.text(xy=(x_min, y_min), text=det['LabelName'], fill=color)
        draw.text(xy=((x_min + x_max) / 2, (y_min + y_max) / 2), text=str(int(pred[i])), fill=color)
        for offset in [-1, 0, 1]:
            draw.rectangle(xy=[x_min + offset, y_min + offset, x_max + offset, y_max + offset],
                           outline=color)
    img.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Visualize detections and acceptance predictions on an image')
    parser.add_argument('path_to_image', type=str, metavar='path_to_image', help='path to image')

    args = parser.parse_args()
    visualize_detection(args.path_to_image)
