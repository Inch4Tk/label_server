import json

class GroundTruthReader:
    def __init__(self, path_to_gt: str):
        """
        Initiate an object representing a ground-truth-data-file.
        Args:
            path_to_gt: Files separated by first hex-value in image-id
            containing the ground-truth-data in json-format.
        """
        self.path_to_gt = path_to_gt
        self.gt_dicts = [{} for _ in range(16)]

        for i in range(16):
            with open('{}_{}.json'.format(path_to_gt, hex(i)[2]), 'r') as f:
                self.gt_dicts[i] = json.load(f)

    def __enter__(self):
        return self

    def get_ground_truth_annotation(self, image_id: str) -> list:
        """
        Get ground truth for an image.
        Args:
            image_id: ID uniquely identifying an image.

        Returns: Ground truth data of the image.
        """
        char0 = int(image_id[0], 16)
        if image_id in self.gt_dicts[char0]:
            return self.gt_dicts[char0][image_id]
        return []
