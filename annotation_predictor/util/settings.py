import os

root_dir = '/home/schererc/IntelliJProjects/label_server'
annotation_predictor_dir = os.path.join(root_dir, 'annotation_predictor')
annotation_predictor_metadata_dir = os.path.join(annotation_predictor_dir, 'metadata')
annotation_predictor_util_dir = os.path.join(annotation_predictor_dir, 'util')
model_dir = os.path.join(root_dir, 'models')

class_ids_oid_file = os.path.join(annotation_predictor_metadata_dir, 'class_ids_oid.json')
class_ids_coco_file = os.path.join(annotation_predictor_metadata_dir, 'class_ids_coco.json')

path_to_test_data = os.path.join(annotation_predictor_metadata_dir,
                                 '2018_08_07_222301_test.tfrecords')

verification_time = 1.8  # time for verifying one annotation
annotation_time = 7  # time for annotating one object via extreme clicking
alpha = 0.5  # minimum IoU for detection to be accepted as correct
