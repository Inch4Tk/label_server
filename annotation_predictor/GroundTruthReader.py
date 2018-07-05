import csv
import json
from collections import OrderedDict

from settings import class_id_file

class GroundTruthReader:
    def __init__(self, cvsfile: str):
        self.gt_file = open(cvsfile)
        self.reader = csv.DictReader(self.gt_file)
        with open(class_id_file) as file:
            self.classID_file = json.load(file)

    def __exit__(self):
        self.gt_file.close()

    def get_ground_truth_annotation(self, image_id: str) -> list:
        ret = []
        found = False

        while not found:
            buffer = next(self.reader)

            # it is assumed that entries in csv files are ordered by image_id which is true for the OpenImages dataset
            while buffer['ImageID'] == image_id:
                found = True
                ret.append(buffer)
                buffer = next(self.reader)
        return ret

    def get_class_from_id(self, bounding_box: OrderedDict) -> str:
        try:
            return self.classID_file[bounding_box['LabelName']]
        except KeyError as e:
            raise KeyError('ImageID does not exist') from e
