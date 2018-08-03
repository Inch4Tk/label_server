import json

class ClassReader:
    def __init__(self, class_id_file):
        """
        Create an object assigning an ID to every available class in a dataset.
        Args:
            class_id_file: File which contains information about available classes in a dataset.
        """
        with open(class_id_file) as file:
            self.class_ids = json.load(file)

    def get_class_from_id(self, id: str) -> str:
        """
        Args:
            id: ID, uniquely identifying a class.

        Returns: Human-readable description of the class.
        """
        try:
            return self.class_ids[id]
        except KeyError as e:
            raise KeyError('ImageID does not exist') from e

    def get_index_of_class(self, label_name: str) -> int:
        """
        Returns the unique index of a class used for defining a one-hot-encoding for the class.

        Args:
            label_name: Human-readable description of a class.

        Returns: Index of the class in the class-id file.
        """
        return list(self.class_ids.keys()).index(label_name)
