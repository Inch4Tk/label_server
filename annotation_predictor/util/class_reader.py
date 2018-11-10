import json
import os

class ClassReader:
    def __init__(self, class_id_file):
        """
        Create an object assigning an ID to every available class in a dataset.
        Args:
            class_id_file: File which contains information about available classes in a dataset.
        """
        self.class_id_file = class_id_file
        if os.path.exists(class_id_file):
            with open(class_id_file) as file:
                self.class_ids = json.load(file)
        else:
            self.class_ids = {}

    def get_class_from_id(self, id: str):
        """
        Args:
            id: ID, uniquely identifying a class.

        Returns: Human-readable description of the class.
        """
        try:
            return self.class_ids[id]
        except KeyError:
            return

    def get_index_of_class_from_id(self, id: str) -> int:
        """
        Returns the unique index of a class used for defining a one-hot-encoding for the class.

        Args:
            id: ID, uniquely identifying a class.

        Returns: Index of the class in the class-id file.
        """
        return list(self.class_ids.keys()).index(id)

    def get_index_of_class_from_label(self, label: str) -> int:
        """
        Returns the unique index of a class used for defining a one-hot-encoding for the class.

        Args:
            label: human-readable label of a class

        Returns: Index of the class in the class-id file.
        """
        if label not in self.class_ids.values():
            return -1

        return list(self.class_ids.values()).index(label)

    def get_key_of_class_from_label(self, label: str) -> int:
        """
        Returns the unique index of a class used for defining a one-hot-encoding for the class.

        Args:
            label: label of a class.

        Returns: Unique ID of the class.
        """
        keys = list(self.class_ids.keys())
        values = list(self.class_ids.values())
        return keys[values.index(label)]

    def add_class_to_file(self, cls: str):
        """
        Adds a new class to the file containing the known classes

        Args:
            cls: name of new class.
        """
        if cls is not None:
            new_class_key = float(len(self.class_ids) + 1)
            self.class_ids[new_class_key] = cls
            with open(self.class_id_file, 'w') as file:
                json.dump(self.class_ids, file)
