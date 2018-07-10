import csv

class GroundTruthReader:
    def __init__(self, cvsfile: str):
        self.cvsfile = cvsfile
        self.gt_file = open(self.cvsfile)
        self.reader = csv.DictReader(self.gt_file)
        self.gt_dict = self.parse_to_dict()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.gt_file.close()

    def parse_to_dict(self) -> dict:
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
        return self.gt_dict[image_id]
