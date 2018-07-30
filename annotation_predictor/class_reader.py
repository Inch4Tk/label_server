import json

class ClassReader:
    def __init__(self, class_id_file):
        with open(class_id_file) as file:
            self.class_ids = json.load(file)

    def get_class_from_id(self, id: str) -> str:
        try:
            return self.class_ids[id]
        except KeyError as e:
            raise KeyError('ImageID does not exist') from e

    def get_index_of_class(self, label_name: str) -> int:
        return list(self.class_ids.keys()).index(label_name)
