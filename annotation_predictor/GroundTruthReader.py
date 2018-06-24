import csv

class GroundTruthReader:
    def __init__(self, cvsfile: str):
        self.reader = csv.DictReader(open(cvsfile))

    def get_ground_truth(self, image_id: str) -> list:
        ret = []
        found = False

        while not found:
            buffer = next(self.reader)

            while buffer['ImageID'] == image_id:
                found = True
                ret.append(buffer)
                buffer = next(self.reader)
        return ret
