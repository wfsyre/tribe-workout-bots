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
