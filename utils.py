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
    N = len(labels)
    ind = np.arange(N)  # the x locations for the groups
    width = 0.35  # the width of the bars: can also be len(x) sequence

    values = np.array(values)
    excellent = values[:, 0]
    good = values[:, 1]
    average = values[:, 2]
    low = values[:, 3]

    p1 = plt.bar(ind, excellent, width)
    p2 = plt.bar(ind, good, width,
                 bottom=excellent)
    p3 = plt.bar(ind, average, width,
                 bottom=good)
    p4 = plt.bar(ind, low, width,
                 bottom=average)

    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)
    plt.xticks(ind, (labels))
    plt.legend((p1[0], p2[0], p3[0], p4[0]), ('Excellent', 'Good', 'Average', 'Low'))
    plt.plot()
    file_name = "feedback_plot.png"
    plt.savefig(file_name)
    return file_name
