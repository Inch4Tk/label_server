import os

from annotation_predictor.util.groundtruth_reader import GroundTruthReader
from annotation_predictor.util.oid_classcode_reader import OIDClassCodeReader
from annotation_predictor.util.util import compute_iou
from settings import alpha

evaluation_record = {}

def evaluate_od_performance(path_to_test_images: str, path_to_gt: str):
    """
    Computes the mAP@alpha for a given test set and the current state of the object
    detector. (modify alpha in settings if necessary)

    Args:
        path_to_test_images: test images
        path_to_gt: Ground-Truth-Data for the test images
    """

    gt_reader = GroundTruthReader(path_to_gt)
    oid_classcode_reader = OIDClassCodeReader()

    highest_iou = 0
    correct = 0
    incorrect = 0

    for image in os.listdir(path_to_test_images):
        image_id = os.path.splitext(image)[0]
        ground_truth = gt_reader.get_ground_truth_annotation(image_id)
        detections = send_od_request(os.path.join(path_to_test_images, image))
        for d in detections:
            for single_det in detections[d]:
                oid_class_code = oid_classcode_reader.get_code_for_human_readable_class(
                    single_det['LabelName'])
                for g in [gt for gt in ground_truth if gt['LabelName'] == oid_class_code]:
                    gt_bb = {'XMin': g['XMin'], 'YMin': g['YMin'], 'XMax': g['XMax'],
                             'YMax': g['YMax']}
                    det_bb = {'XMin': single_det['XMin'], 'YMin': single_det['YMin'],
                              'XMax': single_det['XMax'], 'YMax': single_det['YMax']}
                    iou = compute_iou(gt_bb, det_bb)
                    if iou > highest_iou:
                        highest_iou = iou
                if highest_iou > alpha:
                    correct += 1
                else:
                    incorrect += 1
                highest_iou = 0

    return correct / (correct + incorrect)
