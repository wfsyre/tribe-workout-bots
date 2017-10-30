import os
import urllib.parse
import sys
import json
import urllib.request
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
    # We don't want to reply to ourselves!
    send_debug_message("This is working")
    if data['name'] != 'WORKOUT BOT':
        if '!website' in data['text']:
            send_tribe_message("https://gttribe.wordpress.com/about/")
        elif '!iloveyou' in data['text']:
            send_tribe_message("I love you too %s <3" % data['name'])
        elif '!help' in data['text']:
            send_tribe_message("available commands: !throw, !gym, !website, !ultianalytics")
        elif 'ultianalytics' in data['text']:
            send_tribe_message("url: http://www.ultianalytics.com/app/#/5629819115012096/login || password: %s" % (os.getenv("ULTI_PASS")))
        elif '!gym' in data['text'] or '!throw' in data['text']:
            addition = 1 if "!gym" in data['text'] else 0.5
            if len(data['attachments']) > 0:
                group_members = get_group_info(data['group_id'])
                names = []
                found_attachment = False
                for attachment in data["attachments"]:
                    if attachment['type'] == 'image':
                        send_workout_selfie(data["name"] + " says \"" + data['text'] + "\"", attachment['url'])
                        found_attachment = True
                    if attachment['type'] == 'mentions':
                        for mentioned in attachment['user_ids']:
                            for member in group_members:
                                if member["user_id"] == mentioned:
                                    names.append(member["nickname"])
                if found_attachment:
                    names.append(data['name'])
                    test_db_connection(names, addition)
    return "ok", 200


def send_tribe_message(msg):
    send_message(msg, os.getenv("TRIBE_BOT_ID"))


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


def test_db_connection(names, addition):
    send_debug_message("start")
    urllib.parse.uses_netloc.append("postgres")
    url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    send_debug_message("connected")
    cursor = conn.cursor()
    for name in names:
        cursor.execute(sql.SQL(
            "UPDATE tribe_data SET num_workouts = num_workouts+1, workout_score = workout_score+%s WHERE name = %s;"),
            [addition, name])
    cursor.execute(
        sql.SQL("UPDATE tribe_data SET num_posts = num_posts-6 WHERE {} = %s;").format(sql.Identifier('name')),
        names[0])
    send_debug_message("End")




