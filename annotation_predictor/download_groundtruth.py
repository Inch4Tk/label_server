import os
import urllib.request as urllib

from settings import path_to_test_gt_file, path_to_val_gt_file, path_to_train_gt_file, \
    train_gt_file, test_gt_file, val_gt_file

def download_oid_gt():
    """
    Download groundtruth data from the Open Images Dataset
    """
    url = 'https://storage.googleapis.com/openimages/2018_04/'

    url_to_train_gt = os.path.join(url, 'train', train_gt_file)
    url_to_test_gt = os.path.join('test', test_gt_file)
    url_to_val_gt = os.path.join('validation', val_gt_file)

    file = urllib.URLopener()

    if not os.path.exists(path_to_test_gt_file):
        file.retrieve(os.path.join(url, url_to_test_gt), path_to_test_gt_file)
    if not os.path.exists(path_to_val_gt_file):
        file.retrieve(os.path.join(url, url_to_val_gt), path_to_val_gt_file)
    if not os.path.exists(path_to_train_gt_file):
        file.retrieve(os.path.join(url, url_to_train_gt), path_to_train_gt_file)

if __name__ == '__main__':
    download_oid_gt()
