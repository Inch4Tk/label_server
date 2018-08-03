import csv

class GroundTruthReader:
    def __init__(self, csvfile: str):
        """
        Initiate an object representing a ground-truth-data-file.
        Args:
            csvfile: File containing the ground-truth-data in cvs-format.
        """
        self.csvfile = csvfile
        self.gt_file = open(self.csvfile)
        self.reader = csv.DictReader(self.gt_file)
        self.gt_dict = self.parse_to_dict()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.gt_file.close()

    def parse_to_dict(self) -> dict:
        """
        Read in a csv-file containing ground-truth data and save it in a dict
        """
        result = {}
        for entry in self.reader:
            key = entry['ImageID']
            entry.pop('ImageID')
            if key in result:
                result[key].append(entry)
            else:
                result[key] = [entry]
        return result

    def get_ground_truth_annotation(self, image_id: str) -> list:
        """
        Get ground truth for an image.
        Args:
            image_id: ID uniquely identifying an image.

        Returns: Ground truth data of the image.
        """
        if image_id in self.gt_dict:
            return self.gt_dict[image_id]
        return []
