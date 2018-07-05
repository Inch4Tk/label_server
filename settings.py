import os

root_dir = os.path.dirname(os.path.abspath(__file__))
annotation_predictor_dir = os.path.join(root_dir, 'annotation_predictor')

class_id_file = os.path.join(annotation_predictor_dir, 'class_ids.json')
