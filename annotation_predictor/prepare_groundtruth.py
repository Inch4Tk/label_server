import shutil

from annotation_predictor import convert_oi_gt_to_jsons
from annotation_predictor.concat_detection_records import concat_detection_record
from annotation_predictor.download_groundtruth import download_oid_gt
from settings import path_to_train_gt_file, \
    path_to_test_gt_file, path_to_val_gt_file

def prepare_gt():
    """
    Prepare the metadata directory by downloading and postprocessing the groundtruth data of the
    Open Images Dataset
    """
    download_oid_gt()
    path_to_new_file = concat_detection_record(path_to_train_gt_file, path_to_test_gt_file)
    path_to_newer_file = concat_detection_record(path_to_new_file, path_to_val_gt_file)

    shutil.rmtree(path_to_new_file)

    convert_oi_gt_to_jsons.convert(path_to_newer_file)

if __name__ == '__main__':
    prepare_gt()
