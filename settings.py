import os

# ADAPT
root_dir = '/home/schererc/IntelliJProjects/label_server'

model_dir = os.path.join(root_dir, 'models')

# Annotation Predictor
annotation_predictor_dir = os.path.join(root_dir, 'annotation_predictor')
annotation_predictor_metadata_dir = os.path.join(annotation_predictor_dir, 'metadata')
annotation_predictor_util_dir = os.path.join(annotation_predictor_dir, 'util')
known_class_ids_annotation_predictor = os.path.join(annotation_predictor_metadata_dir,
                                                    'known_class_ids.json')
path_to_label_performance_log = os.path.join(annotation_predictor_metadata_dir,
                                             'label_performance_log.json')
path_to_map_log = os.path.join(annotation_predictor_metadata_dir,
                               'model_map_log.json')

train_gt_file = 'train-annotations-bbox.csv'
test_gt_file = 'test-annotations-bbox.csv'
val_gt_file = 'validation-annotations-bbox.csv'

path_to_train_gt_file = os.path.join(annotation_predictor_metadata_dir, train_gt_file)
path_to_test_gt_file = os.path.join(annotation_predictor_metadata_dir, test_gt_file)
path_to_val_gt_file = os.path.join(annotation_predictor_metadata_dir, val_gt_file)

# ADAPT
path_to_test_data = os.path.join(annotation_predictor_metadata_dir,
                                 '2018_11_13_195357_test.tfrecords')
path_to_model_evaluation_record = os.path.join(annotation_predictor_metadata_dir,
                                               '2018_11_13_195305_evaluation.json')

# Object Detector
path_to_od_dir = os.path.join(root_dir, 'object_detector')
path_to_od_metadata_dir = os.path.join(path_to_od_dir, 'metadata')
path_to_od_test_data = os.path.join(path_to_od_metadata_dir, 'test')
path_to_od_lib = os.path.join(root_dir, 'od_models', 'research', 'object_detection')
path_to_pipeline_config = os.path.join(path_to_od_metadata_dir, 'pipeline.config')
class_ids_od = os.path.join(path_to_od_metadata_dir, 'class_ids.json')
oid_classcodes = os.path.join(path_to_od_metadata_dir, 'oid_classcodes.json')
oid_classcodes_inverted = os.path.join(path_to_od_metadata_dir, 'oid_classcodes_inverted.json')
path_to_known_class_pbtxt = os.path.join(path_to_od_metadata_dir, 'class_ids.pbtxt')
path_to_od_train_record = os.path.join(path_to_od_metadata_dir, 'train.record')

# ADAPT
path_to_od_test_data_gt = os.path.join(path_to_od_test_data, '2018_11_04_133201.json')

# Constants
verification_time = 1.8  # time for verifying one annotation
annotation_time = 7  # time for annotating one object via extreme clicking
alpha = 0.5  # minimum IoU for detection to be accepted as correct
