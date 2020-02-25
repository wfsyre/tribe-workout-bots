import matplotlib.pyplot as plt
import matplotlib
import numpy as np


def stringFromSeconds(seconds):
    if seconds < 0:
        return seconds, " seconds. You missed it, better luck next year."
    else:
        days = seconds / 60 / 60 / 24
        fracDays = days - int(days)
        hours = fracDays * 24
        fracHours = hours - int(hours)
        minutes = fracHours * 60
        fracMinutes = minutes - int(minutes)
        seconds = fracMinutes * 60
        return "%d days, %d hours, %d minutes, %d seconds" % (days, minutes, hours, seconds)


def generate_trending_bargraph(people_counts):
    labels = list(people_counts.keys())
    first_names = [whole_name.split(" ")[0] for whole_name in people_counts.keys()]
    values = [people_counts[x] for x in labels]
    values, first_names = (list(t) for t in zip(*sorted(zip(values, first_names))))
    x = np.arange(len(first_names))
    width = 0.5
    fig, ax = plt.subplots()
    rects1 = ax.bar(x, values, width)
    ax.set_ylabel('Number of Workouts')
    ax.set_title('Workouts In The Last Month')
    ax.set_xticks(x)
    ax.set_xticklabels(first_names)
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
    plt.plot()
    file_name = "plot.png"
    plt.savefig(file_name)
    return file_name


def generate_bargraph(labels, values, title, x_label, y_label):
    x = np.arange(len(labels))
    width = 0.5
    fig, ax = plt.subplots()
    rects1 = ax.bar(x, values, width)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
    plt.plot()
    file_name = "plot.png"
    plt.savefig(file_name)
    return file_name

def generate_feedback_bargraph(labels, values, title, x_label, y_label):
    width = 0.35  # the width of the bars: can also be len(x) sequence
    true_values = []
    true_lables = []
    for i in range(len(values)):
        if len(values[i]) == 5 and np.sum(np.array(values[i][0:4])) > 0:
            print(values[i])
            true_lables.append(labels[i])
            true_values.append(values[i])
    labels = true_lables
    values = np.squeeze(np.array(true_values))
    max_tick = np.max(values)
    N = len(labels)
    ind = np.arange(N)  # the x locations for the groups
    fig, ax = plt.subplots()
    excellent = values[:, 0]
    good = values[:, 1]
    average = values[:, 2]
    low = values[:, 3]

    matrix = np.vstack((excellent, good, average, low))
    weights = np.array([4, 3, 2, 1])
    sums = np.sum(matrix, axis=0)
    result = weights.dot(matrix)
    true_avg = result / sums
    print("True Average: ", true_avg)

    p1 = ax.plot(ind, low, label='low')
    p2 = ax.plot(ind, average, label='average')
    p3 = ax.plot(ind, good, label='good')
    p4 = ax.plot(ind, excellent, label='excellent')
    p5 = ax.plot(ind, true_avg, label='average score')

    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)
    plt.xticks(ind, labels)
    plt.yticks(np.arange(0, max_tick, 1))
    plt.legend((p5[0], p4[0], p3[0], p2[0], p1[0]), ('Average score', 'Excellent', 'Good', 'Average', 'Low'))
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
    ax.yaxis().grid(True)
    ax.xaxis().grid(True)
    plt.plot()
    file_name = "feedback_plot.png"
    plt.savefig(file_name)
    return file_name


def get_average_intensity_score(labels, values):
    true_values = []
    true_lables = []
    for i in range(len(values)):
        if len(values[i]) == 5:
            true_lables.append(labels[i])
            true_values.append(values[i])
    labels = true_lables
    values = np.squeeze(np.array(true_values))
    print(values)

    excellent = values[:, 0]
    good = values[:, 1]
    average = values[:, 2]
    low = values[:, 3]

    total = 4 * np.sum(excellent) + 3 * np.sum(good) + 2 * np.sum(average) + np.sum(low)
    total = total / (np.sum(excellent) + np.sum(good) + np.sum(average) + np.sum(low))

    matrix = np.vstack((excellent, good, average, low))
    weights = np.array([4, 3, 2, 1])
    sums = np.sum(matrix, axis=0)
    result = weights.dot(matrix)
    return total, result / sums, labels


# def main():
#     values = [[[0], [0], [0], [0], [0], [34]], [[1], [13], [6], [0], [0], [15]], [[5], [8], [2], [1], [18]],
#          [[4], [11], [8], [0], [11]]]
#     labels = ['01/14/2020', '01/15/2020', '01/16/2020', '01/21/2020']
#     total, per_day, labels = get_average_intensity_score(labels, values)
#     print(per_day)
#     print(total)
#     print(labels)
#
#
# if __name__ == '__main__':
#     main()
