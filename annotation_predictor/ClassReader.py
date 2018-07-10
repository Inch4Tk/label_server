import json
from collections import OrderedDict

from settings import class_id_file

class ClassReader:
    def __init__(self):
        with open(class_id_file) as file:
            self.class_ids = json.load(file)

    def get_class_from_id(self, bounding_box: OrderedDict) -> str:
        try:
            return self.class_ids[bounding_box['LabelName']]
        except KeyError as e:
            raise KeyError('ImageID does not exist') from e

    def get_index_of_class(self, label_name: str) -> int:
        return list(self.class_ids.keys()).index(label_name)
