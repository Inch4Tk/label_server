import os

root_dir = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(root_dir, 'instance', 'images')
annotation_predictor_dir = os.path.join(root_dir, 'annotation_predictor')
annotation_predictor_metadata_dir = os.path.join(annotation_predictor_dir, 'metadata')

class_id_file = os.path.join(annotation_predictor_metadata_dir, 'class_ids.json')
