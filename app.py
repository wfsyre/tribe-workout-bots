import json
import os
import urllib.parse
import sys
import urllib.request
import time
import psycopg2
import requests
from datetime import datetime
from slackclient import SlackClient
from psycopg2 import sql

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    GYM_POINTS = 1.0
    TRACK_POINTS = 1.0
    THROW_POINTS = 0.5
    SWIM_POINTS = 1.0
    PICKUP_POINTS = 0.5
    BIKING_POINTS = 1.0
    BOT_CHANNEL = "CBJAJPZ8B"
    data = request.get_json()
    if 'text' in list(data['event'].keys()):
        lower_text = data['event']['text'].lower()
    if data['type'] == "url_verification":
        return jsonify({'challenge': data['challenge']})


    if 'username' not in list(data['event'].keys()):    #messages without attachments go here
        lower_text = data['event']['text'].lower()
        names, ids = get_names_ids_from_message(data['event']['text'])
        repeat = add_num_posts([data['event']['user']], data['event_time'])
        if not repeat:
            if "!leaderboard" in lower_text:
                print_stats(3, True)
            if '!workouts' in lower_text:  # display the leaderboard for who works out the most
                print_stats(2, True)
            if '!talkative' in lower_text:  # displays the leaderboard for who posts the most
                print_stats(1, True)
            if '!handsome' in lower_text:  # displays the leaderboard for who posts the most
                print_stats(1, True)
            if '!heatcheck' in lower_text:
                send_tribe_message("Kenta wins")
            if '!regionals' in lower_text:
                now = datetime.now()
                regionals = datetime(2019, 4, 28, 8, 0, 0)
                until = regionals - now
                send_tribe_message("regionals is in " + stringFromSeconds(until.total_seconds()))
            if '!' in lower_text:
                like_message(data['event']['channel'], data['event']['ts'])
            if '!subtract' in lower_text and data['event']['channel'] == BOT_CHANNEL:
                send_debug_message("SUBTRACTING: " + lower_text[-3:] + " FROM: " + str(names))
                num = subtract_from_db(names, float(lower_text[-3:]), ids)
    

    elif data['event']['username'] != "Workout Bot":  #messages with attachments go here
        if data['event']['subtype'] == 'file_share':
            print("found an uploaded image")
            lower_text = data['event']['text'].lower()
            names, ids = get_names_ids_from_message(data['event']['text'])
            print("names ", names, "ids", ids)
            repeat = add_num_posts([data['event']['user']], data['event_time'])
            num = -1
            if not repeat:
                if "!gym" in lower_text:
                    print("gym found")
                    num = add_to_db(names, GYM_POINTS, ids)
                if "!track" in lower_text:
                    print("track found")
                    num = add_to_db(names, TRACK_POINTS, ids)
                if "!throw" in lower_text:
                    print("throw found")
                    num = add_to_db(names, THROW_POINTS, ids)
                if "!swim" in lower_text:
                    print("swim found")
                    num = add_to_db(names, SWIM_POINTS, ids)
                if "!pickup" in lower_text:
                    print("pickup found")
                    num = add_to_db(names, PICKUP_POINTS, ids)
                if "!bike" in lower_text:
                    print("bike found")
                    num = add_to_db(names, BIKING_POINTS, ids)
                if "!test" in lower_text:
                    print("test found")
                    num = add_to_db(names, 0, ids)
            print("NUM: ", num)
            if num == len(names):
                like_file(data['event']['file']['id']) 
    else:
        print("Don't respond to myself")
    return "ok", 200


def send_tribe_message(msg):
    send_message(msg, chan="#random")

def get_names_ids_from_message(lower_text):
    ids = parse_text_for_mentions(lower_text)
    names = match_names_to_ids(ids)
    return names, ids


def add_num_posts(mention_id, event_time):
    name = match_names_to_ids(mention_id)[0]
    # "UPDATE tribe_data SET num_posts=num_posts+1, WHERE name = 'William Syre' AND last_time != "
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "UPDATE tribe_data SET num_posts=num_posts+1, "
            + "slack_id=%s, "
            + "last_time = %s "
            + "WHERE name = %s AND last_time != %s"), [mention_id[0], event_time, name, event_time])
        if cursor.rowcount == 0:
            conn.commit()
            cursor.close()
            conn.close()
            send_debug_message("Found a repeat slack post")
            return True
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return False
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)


def handle_workouts(data, addition):
    names, ids = get_names_ids_from_message(data, True)
    if names is not None and ids is not None:
        num = add_to_db(names, addition, ids)
    if num == len(names):
        like_message(data['group_id'], data['id'])


def print_stats(datafield, rev):
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "SELECT * FROM tribe_data WHERE workout_score > -1.0"), )
        leaderboard = cursor.fetchall()
        leaderboard.sort(key=lambda s: s[datafield], reverse=rev)  # sort the leaderboard by score descending
        string1 = "Top 15:\n"
        string2 = "Everyone Else:\n"
        for x in range(0, 15):
            string1 += '%d) %s with %.1f points \n' % (x + 1, leaderboard[x][0], leaderboard[x][datafield])
        for x in range(15, len(leaderboard)):
            string2 += '%d) %s with %.1f points \n' % (x + 1, leaderboard[x][0], leaderboard[x][datafield])
        send_tribe_message(string1)  # need to split it up into 2 because groupme has a max message length for bots
        send_tribe_message(string2)
        cursor.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)


def send_message(msg, chan="#bot_testing"):
    slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
    sc = SlackClient(slack_token)
    sc.api_call("chat.postMessage",channel=chan, text=msg)

def send_debug_message(msg):
    send_message(msg, chan="#bot_testing")

def log(msg):
    print(str(msg))
    sys.stdout.flush()


def get_group_info():
    url = "https://slack.com/api/users.list?token=" + os.getenv('BOT_OATH_ACCESS_TOKEN')
    json = requests.get(url).json()
    return json

def parse_text_for_mentions(text):
    indicies = []
    mention_ids = []
    i = 0
    while(i < len(text)):
        temp = text.find('@', i)
        if temp == -1:
            i = len(text)
        else:
            indicies.append(temp)
            i = temp + 1
    for index in indicies:
        mention_ids.append(text[index + 1:text.find('>', index)])
    return mention_ids

def match_names_to_ids(mention_ids):
    mention_names = []
    info = get_group_info()
    for id in mention_ids:
        for member in info['members']:
            if member['id'] == id:
                mention_names.append(member['real_name'])
    return mention_names
   


def add_to_db(names, addition, ids):  # add "addition" to each of the "names" in the db
    cursor = None
    conn = None
    num_committed = 0
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        for x in range(0, len(names)):
            cursor.execute(sql.SQL(
                "SELECT workout_score FROM tribe_data WHERE name = %s"), (str(names[x]),))
            score = cursor.fetchall()[0][0]
            score = int(score)
            if score != -1:
                cursor.execute(sql.SQL(
                    "UPDATE tribe_data SET num_workouts = num_workouts+1, workout_score = workout_score+%s, last_post = "
                    "now(), slack_id=%s WHERE name = %s"),
                    (str(addition), ids[x], names[x],))
                # if cursor.rowcount == 0:  # If a user does not have an id yet
                #     cursor.execute(sql.SQL(
                #         "UPDATE tribe_data SET num_workouts = num_workouts+1, workout_score = workout_score+%s, last_post "
                #         "= now() WHERE name = %s"),
                #         (str(addition), names[x],))
                #     send_debug_message("%s does not have an id yet" % names[x])
                conn.commit()
                send_debug_message("committed %s" % names[x])
                num_committed += 1
            else:
                send_debug_message("invalid workout poster found " + str(score))
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        return num_committed


def add_hydration(data, addition):
    return None #does not work for slack
    cursor = None
    conn = None
    num_committed = 0
    names, ids = get_names_ids_from_message(data, True)
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        for x in range(0, len(names)):
            cursor.execute(sql.SQL(
                "UPDATE tribe_water SET num_liters = num_liters+%s WHERE id = %s"),
                (str(addition), ids[x],))
            if cursor.rowcount == 0:  # If a user does not have an id yet
                cursor.execute(sql.SQL(
                    "UPDATE tribe_water SET num_liters = num_liters+%s, id = %s WHERE name = %s"),
                    (str(addition), ids[x], names[x],))
                send_debug_message("%s does not have an id yet" % names[x])
            if cursor.rowcount == 0:  # user is not in the db yet
                cursor.execute(sql.SQL("INSERT INTO tribe_water VALUES (%s, 1, %s)"), (names[x], ids[x],))
            conn.commit()
            send_debug_message("committed %s" % names[x])
            num_committed += 1
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        if len(names) == num_committed:
            like_message(data['group_id'], data['id'])
        return num_committed


def print_water():
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "SELECT * FROM tribe_water WHERE num_liters > -1.0"), )
        leaderboard = cursor.fetchall()
        leaderboard.sort(key=lambda s: s[1], reverse=True)  # sort the leaderboard by score descending
        string1 = "Top 15:\n"
        string2 = "Everyone Else:\n"
        for x in range(0, 15):
            if x < len(leaderboard):
                string1 += '%d) %s with %d points \n' % (x + 1, leaderboard[x][0], leaderboard[x][1])
        if len(leaderboard) > 15:
            for x in range(15, len(leaderboard)):
                string2 += '%d) %s with %d points \n' % (x + 1, leaderboard[x][0], leaderboard[x][1])
        send_tribe_message(string1)  # need to split it up into 2 because groupme has a max message length for bots
        if len(leaderboard) > 15:
            send_tribe_message(string2)
        cursor.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)


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


def like_message(chan, time):
    slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
    sc = SlackClient(slack_token)
    res = sc.api_call("reactions.add", name='robot_face', channel=chan, timestamp=time)

def like_file(f):
    slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
    sc = SlackClient(slack_token)
    res = sc.api_call("reactions.add", name='robot_face', file=f)


def subtract_from_db(names, subtraction, ids):  # subtract "subtraction" from each of the "names" in the db
    cursor = None
    conn = None
    num_committed = 0
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        for x in range(0, len(names)):
            cursor.execute(sql.SQL(
                "UPDATE tribe_data SET workout_score = workout_score - %s WHERE name = %s"),
                [subtraction, names[x]])
            conn.commit()
            send_debug_message("subtracted %s" % names[x])
            num_committed += 1
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        return num_committed

