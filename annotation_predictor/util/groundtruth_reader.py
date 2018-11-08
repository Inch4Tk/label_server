import json
import os

class GroundTruthReader:
    def __init__(self, path_to_gt: str):
        """
        Initiate an object representing a ground-truth-data-file.
        Args:
            path_to_gt: Files separated by first hex-value in image-id
            containing the ground-truth-data in json-format.
        """
        self.path_to_gt = path_to_gt
        self.gt_dict = [{} for _ in range(16)]

        if os.path.splitext(os.path.basename(path_to_gt))[1] != '.json':
            for i in range(16):
                with open('{}_{}.json'.format(path_to_gt, hex(i)[2]), 'r') as f:
                    self.gt_dict[i] = json.load(f)
        else:
            with open(path_to_gt, 'r') as f:
                self.gt_dict = json.load(f)

    def __enter__(self):
        return self

    def get_ground_truth_annotation(self, image_id: str) -> list:
        """
        Get ground truth for an image.
        Args:
            image_id: ID uniquely identifying an image.

        Returns: Ground truth data of the image.
        """
        if os.path.splitext(os.path.basename(self.path_to_gt))[1] != '.json':
            char0 = int(image_id[0], 16)
            if image_id in self.gt_dict[char0]:
                return self.gt_dict[char0][image_id]
            return []

        else:
            if image_id in self.gt_dict:
                return self.gt_dict[image_id]
            return []
