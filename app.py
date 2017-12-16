import os
import urllib.parse
import sys
import json
import urllib.request
import datetime
import psycopg2
from psycopg2 import sql

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log('Recieved {}'.format(data))
    # We don't want to reply to ourselves
    if data['name'] != 'WORKOUT BOT' and data['name'] != 'TEST':
        GYM_POINTS = 1.0
        TRACK_POINTS = 1.0
        THROW_POINTS = 0.5
        SWIM_POINTS = 1.0
        PICKUP_POINTS = 0.5
        BIKING_POINTS = 1.0
        try:
            #set up connection to the database
            urllib.parse.uses_netloc.append("postgres")
            url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
            conn = psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
            )
            cursor = conn.cursor()
            #add 1 to the number of posts of the person that posted
            cursor.execute(sql.SQL(
                "UPDATE tribe_data SET num_posts = num_posts+1 WHERE id = %s"),
                (data['user_id'], ))
            if cursor.rowcount == 0: #No id but possibly has a name
                cursor.execute(sql.SQL(
                    "UPDATE tribe_data SET num_posts = num_posts+1, id = %s WHERE name = %s"),
                    (data['user_id'], data['name'],))
                send_debug_message("gave an id to %s" % data['name'])
            if cursor.rowcount == 0: #Is not present in the database and needs to be added
                cursor.execute(sql.SQL("INSERT INTO tribe_data VALUES (%s, 1, 0, 0, now()), %s"), (data['name'], data['user_id'],))
                send_debug_message("added %s to the group" % data['name'])
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as error:
            send_debug_message(error)
        text = data['text'].lower()
        if '!website' in text:
            #send the website information to the groupme
            send_tribe_message("https://gttribe.wordpress.com/about/")
        elif '!iloveyou' in text:
            #special command for Stephen Mock
            send_tribe_message("I love you too %s <3" % data['name'])
        elif '!help' in text:
            #Special command for Jeffrey Minowa
            send_tribe_message("available commands: !throw, !gym, !swim, !track, !bike, !pickup, !website, !ultianalytics, !leaderboard, !workouts, !talkative")
        elif 'ultianalytics' in text:
            #get the ultianalytics password
            send_tribe_message("url: http://www.ultianalytics.com/app/#/5629819115012096/login || password: %s" % (os.getenv("ULTI_PASS")))
        elif '!gym' in text:
            handle_workouts(data, GYM_POINTS)
        elif '!throw' in text:
            handle_workouts(data, THROW_POINTS)
        elif '!swim' in text:
            handle_workouts(data, SWIM_POINTS)
        elif '!track' in text:
            handle_workouts(data, TRACK_POINTS)
        elif '!bike' in text:
            handle_workouts(data, BIKING_POINTS)
        elif '!pickup' in text:
            handle_workouts(data, PICKUP_POINTS)
        elif '!leaderboard' in text: #post the leaderboard in the groupme
            print_stats(3, True)
        elif '!workouts' in text: #display the leaderboard for who works out the most
            print_stats(2, True)
        elif '!talkative' in text:  # displays the leaderboard for who posts the most
            print_stats(1, True)
        elif '!reset' in text and data['name'] == 'William Syre':
            send_tribe_message("Final leaderboard is:")
            print_stats(3, True)
            try:
                urllib.parse.uses_netloc.append("postgres")
                url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
                conn = psycopg2.connect(
                    database=url.path[1:],
                    user=url.username,
                    password=url.password,
                    host=url.hostname,
                    port=url.port
                )
                cursor = conn.cursor()
                # add 1 to the number of posts of the person that posted
                cursor.execute(sql.SQL(
                    "UPDATE tribe_data SET workout_score = 0, num_workouts = 0, last_post = now() WHERE workout_score > -1"))
                conn.commit()
                cursor.close()
                conn.close()
                send_debug_message("workouts have been purged")
            except Exception as error:
                send_debug_message(error)
    return "ok", 200


def send_tribe_message(msg):
    send_message(msg, os.getenv("TRIBE_BOT_ID"))

def handle_workouts(data, addition):
    if len(data['attachments']) > 0:
        # attachments are images or @mentions
        ids = []
        group_members = get_group_info(data['group_id'])  # should get the groupme names of all members in the group.
        names = []
        found_attachment = False  # This will track whether we found an image or not, which is required
        for attachment in data["attachments"]:
            if attachment['type'] == 'image':
                send_workout_selfie(data["name"] + " says \"" + data['text'] + "\"",
                                    attachment['url'])  # send the workout selfie to the other groupme
                found_attachment = True
            if attachment['type'] == 'mentions':  # grab all the people @'d in the post to include them
                send_debug_message(str(attachment['user_ids']))
                for mentioned in attachment['user_ids']:
                    for member in group_members:
                        if member["user_id"] == mentioned:
                            names.append(member["nickname"])
                            ids.append(member["user_id"])
        if found_attachment:  # append the poster to the list of names to be updated in the database
            names.append(data['name'])
            ids.append(data['user_id'])
            send_debug_message(str(names))
            add_to_db(names, addition, ids)

def print_stats(datafield, rev):
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
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


def send_message(msg, bot_ID):
    url = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': bot_ID,
        'text': msg,
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()


def send_workout_selfie(msg, image_url):
    send_message(msg, os.getenv("WORKOUT_BOT_ID"))
    send_message(image_url, os.getenv("WORKOUT_BOT_ID"))


def send_debug_message(msg):
    send_message(msg, os.getenv("TEST_BOT_ID"))


def log(msg):
    print(str(msg))
    sys.stdout.flush()


def get_group_info(group_id):
    with urllib.request.urlopen("https://api.groupme.com/v3/groups/%s?token=%s" % (
    group_id, os.getenv("ACCESS_TOKEN"))) as response:
        html = response.read()
    dict = parse_group_for_members(html)
    return dict["response"]["members"]


def parse_group_for_members(html_string):
    return json.loads(html_string)


def add_to_db(names, addition, ids): #add "addition" to each of the "names" in the db
    cursor = None
    conn = None
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
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
                "UPDATE tribe_data SET num_workouts = num_workouts+1, workout_score = workout_score+%s, last_post = now() WHERE id = %s"),
                (str(addition), ids[x],))
            if cursor.rowcount == 0: #If a user does not have an id yet
                cursor.execute(sql.SQL(
                    "UPDATE tribe_data SET num_workouts = num_workouts+1, workout_score = workout_score+%s, last_post = now(), id = %s WHERE name = %s"),
                    (str(addition), names[x], ids[x],))
                send_debug_message("%s does not have an id yet" % names[x])
            conn.commit()
            send_debug_message("committed %s" % names[x])
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()




