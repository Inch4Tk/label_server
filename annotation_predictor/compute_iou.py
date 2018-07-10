from collections import OrderedDict

def compute_iou(det_a: OrderedDict, det_b: OrderedDict) -> float:
    bbA = [float(det_a['XMin']), float(det_a['YMin']), float(det_a['XMax']), float(det_a['YMax'])]
    bbB = [float(det_b['XMin']), float(det_b['YMin']), float(det_b['XMax']), float(det_b['YMax'])]

    x_min = max(bbA[0], bbB[0])
    y_min = max(bbA[1], bbB[1])
    x_max = min(bbA[2], bbB[2])
    y_max = min(bbA[3], bbB[3])

    intersection_area = max(0.0, x_max - x_min) * max(0.0, y_max - y_min)

    a_area = (bbA[0] - bbA[2]) * (bbA[1] - bbA[3])
    b_area = (bbB[0] - bbB[2]) * (bbB[1] - bbB[3])

    iou = round(intersection_area / float(a_area + b_area - intersection_area), 5)

    return iou
