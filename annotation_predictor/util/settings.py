import os

annotation_predictor_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
annotation_predictor_metadata_dir = os.path.join(annotation_predictor_dir, 'metadata')
annotation_predictor_util_dir = os.path.join(annotation_predictor_dir, 'util')
model_dir = os.path.join(annotation_predictor_dir, 'models')

class_ids_oid_file = os.path.join(annotation_predictor_metadata_dir, 'class_ids_oid.json')
class_ids_coco_file = os.path.join(annotation_predictor_metadata_dir, 'class_ids_coco.json')

verification_time = 1.8  # time for verifying one annotation
annotation_time = 7  # time for annotating one object via extreme clicking
alpha = 0.5  # minimum IoU for detection to be accepted as correct
