def compute_iou(detA, detB):
    bbA = [float(detA['XMin']), float(detA['YMin']), float(detA['XMax']), float(detA['YMax'])]
    bbB = [float(detB['XMin']), float(detB['YMin']), float(detB['XMax']), float(detB['YMax'])]

    x_min = max(bbA[0], bbB[0])
    y_min = max(bbA[1], bbB[1])
    x_max = min(bbA[2], bbB[2])
    y_max = min(bbA[3], bbB[3])

    intersection_area = max(0.0, x_max - x_min) * max(0.0, y_max - y_min)

    a_area = (bbA[0] - bbA[2]) * (bbA[1] - bbA[3])
    b_area = (bbB[0] - bbB[2]) * (bbB[1] - bbB[3])

    iou = round(intersection_area / float(a_area + b_area - intersection_area), 5)

    return iou
