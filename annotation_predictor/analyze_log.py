import json
from statistics import median

import matplotlib.pyplot as plt
import numpy as np

from settings import path_to_label_performance_log, path_to_map_log

def analyze_log():
    """
    Analyze the logging data which gets generated during usage of the model.
    This prints some relevant values and generates figures which discribe the change in performance
    of the object detector and the average times for different annotation tasks.
    """
    with open(path_to_label_performance_log, 'r') as f:
        label_log = json.load(f)

    with open(path_to_map_log, 'r') as f:
        model_log = json.load(f)

    falsified = [x for x in label_log if x[1] is -2]
    manual_annot = [x for x in label_log if x[1] is -1 or x[1] is 1]
    manual = [x for x in label_log if x[1] is 0]
    verified = [x for x in label_log if x[1] is 2]

    nr_labels = len(label_log)
    print('Nr of User Actions: {}'.format(nr_labels))
    print('Of which were verifications: {} (Percentage: {})'.format(len(verified),
                                                                    len(verified) / nr_labels))
    print('Of which were falsifications: {} (Percentage: {})'.format(len(falsified),
                                                                     len(falsified) / nr_labels))
    print('Of which were manual annotations with annotation proposal: {} (Percentage: {})'.format(
        len(manual_annot), len(manual_annot) / nr_labels))
    print('Of which were purely manual: {} (Percentage: {})'.format(len(manual),
                                                                    len(manual) / nr_labels))

    print('Percentage of successful annotation proposals: {}'.format(
        len([x for x in label_log if x[1] is 1]) / len(manual_annot)))

    times = []

    for i, l in enumerate(label_log[:-1]):
        time = label_log[i + 1][0] - label_log[i][0]

        # sort out unrealistic times
        if 100 < time < 15000:
            times.append([label_log[i + 1][1], time])

    print('Hours of labeling: {}'.format(sum([x[1] for x in times]) / 1000 / 60 / 60))

    print('Average Time per label: {}'.format(
        sum([t[1] for t in times]) / len([t for t in times if t[0] != -2]) / 1000))

    time_falsify = round(
        sum([t[1] for t in times if t[0] is -2]) / len([t for t in times if t[0] is -2]), 3)
    time_wrong_manual = round(sum([t[1] for t in times if t[0] is -1]) / len(
        [t for t in times if t[0] is -1]), 3)
    time_manual = round(
        sum([t[1] for t in times if t[0] is 0]) / len([t for t in times if t[0] is 0]), 3)
    time_right_manual = round(sum([t[1] for t in times if t[0] is 1]) / len(
        [t for t in times if t[0] is 1]), 3)
    time_verify = round(
        sum([t[1] for t in times if t[0] is 2]) / len([t for t in times if t[0] is 2]), 3)
    time_annot_manual = round(
        sum([t[1] for t in times if (t[0] is 1 or t[0] is -1)]) / len(
            [t[1] for t in times if (t[0] is 1 or t[0] is -1)]), 3)

    median_falsify = median([t[1] for t in times if t[0] is -2])
    median_annot_manual = median([t[1] for t in times if (t[0] is -1 or t[0] is 1)])
    median_manual = median([t[1] for t in times if t[0] is 0])
    median_verify = median([t[1] for t in times if t[0] is 2])

    plt.title('mAP for each training iteration')
    plt.xlabel('Iteration')
    plt.ylabel('mAP')
    plt.plot(range(len(model_log)), [x[0] for x in model_log], label='mAP@2')
    plt.plot(range(len(model_log)), [x[1] for x in model_log], label='mAP@5')
    plt.plot(range(len(model_log)), [x[2] for x in model_log], label='mAP@10')
    plt.legend()
    plt.show()

    width = 0.3
    ax = plt.subplot(111)
    x = np.array([1, 2, 3, 4])
    x_ticks = ['Falsify', 'Manual with Proposal', 'Manual', 'Verify']
    plt.xticks(x, x_ticks)
    ax.bar(x - width / 2,
           [time_falsify, (time_wrong_manual + time_right_manual) / 2, time_manual, time_verify],
           width=width, color='b', align='center', label='Mean Time')
    ax.bar(x + width / 2,
           [median_falsify, median_annot_manual, median_manual,
            median_verify], width=width, color='r', align='center', label='Median Time')
    ax.tick_params(axis='x', pad=10)
    plt.ylabel('Time in ms')
    plt.text(x[0] - width, - 250, round(time_falsify))
    plt.text(x[0] + 0.05, - 250, round(median_falsify))
    plt.text(x[1] - width, - 250, round(time_annot_manual))
    plt.text(x[1] + 0.05, - 250, round(median_annot_manual))
    plt.text(x[2] - width, - 250, round(time_manual))
    plt.text(x[2] + 0.05, - 250, round(median_manual))
    plt.text(x[3] - width, - 250, round(time_verify))
    plt.text(x[3] + 0.05, - 250, round(median_verify))
    plt.legend()
    plt.show()

if __name__ == '__main__':
    analyze_log()
