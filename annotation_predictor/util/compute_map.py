import argparse
import os

from annotation_predictor.util.groundtruth_reader import GroundTruthReader
from annotation_predictor.util.oid_classcode_reader import OIDClassCodeReader
from annotation_predictor.util.util import compute_iou
from object_detector.send_od_request import send_od_request
from settings import alpha

evaluation_record = {}

def compute_map(path_to_test_images: str, path_to_gt: str, map_at: int):
    """
    Computes the mAP at a given valuefor a given test set and and the current state of the object
    detector. (modify alpha in settings if necessary)

    Args:
        path_to_test_images: test images
        path_to_gt: Ground-Truth-Data for the test images
        map_at: decides at which value the mAP is computed
    """

    gt_reader = GroundTruthReader(path_to_gt)
    oid_classcode_reader = OIDClassCodeReader()
    mAP = 0
    nr_examples = 0

    for image in os.listdir(path_to_test_images):
        image_id = os.path.splitext(image)[0]
        ground_truth = gt_reader.get_ground_truth_annotation(image_id)
        detections = send_od_request(os.path.join(path_to_test_images, image))
        for d in detections:
            nr_examples += 1
            correct = 0
            for single_det in detections[d][:map_at]:
                oid_class_code = oid_classcode_reader.get_code_for_human_readable_class(
                    single_det['LabelName'])
                for g in [gt for gt in ground_truth if gt['LabelName'] == oid_class_code]:
                    gt_bb = {'XMin': g['XMin'], 'YMin': g['YMin'], 'XMax': g['XMax'],
                             'YMax': g['YMax']}
                    det_bb = {'XMin': single_det['XMin'], 'YMin': single_det['YMin'],
                              'XMax': single_det['XMax'], 'YMax': single_det['YMax']}
                    iou = compute_iou(gt_bb, det_bb)
                    if iou > alpha:
                        correct += 1
                        break

            mAP += correct / map_at

    return mAP / nr_examples

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create and save an evaluation record for the object detection network')
    parser.add_argument('path_to_test_images', type=str, metavar='path_to_images',
                        help='path to detection record')
    parser.add_argument('--path_to_gt', type=str,
                        help='path to ground truth data')
    parser.add_argument('--map_at', type=int,
                        help='decides at which value the mAP is computed')
    args = parser.parse_args()

    compute_map(args.path_to_test_images, args.path_to_gt, args.map_at)
