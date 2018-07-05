import csv

class GroundTruthReader:
    def __init__(self, cvsfile: str):
        self.cvsfile = cvsfile
        self.gt_file = open(self.cvsfile)
        self.reader = csv.DictReader(self.gt_file)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
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
