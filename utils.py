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
    values = [people_counts[x] for x in labels]
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots()
    rects1 = ax.bar(x, values, width)
    ax.set_ylabel('Number of Workouts')
    ax.set_title('Workouts In The Last Month')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.plot()
    file_name = "plot.png"
    plt.savefig(file_name)
    return file_name

