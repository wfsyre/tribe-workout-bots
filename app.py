import os
import sys
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log('Recieved {}'.format(data))

    # We don't want to reply to ourselves!
    if data['name'] != 'TEST':
        msg = '{}, you sent "{}".'.format(data['name'], data['text'])
        send_message(msg)
        if len(data['attachments']) > 0:
            group_members = get_group_info(data['group_id'])
            names = []
            for attachment in data["attachments"]:
                if attachment['type'] == 'mentions':
                    for user in attachment['user_ids']:
                        for member in group_members["members"]:
                            if user == member["user_id"]:
                                names.append(member["nickname"])
            send_message(str(names))
    return "ok", 200


def send_message(msg):
    url = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': msg,
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()


def log(msg):
    print(str(msg))
    sys.stdout.flush()

def get_group_info(group_id):
    send_message(os.getenv("ACCESS_TOKEN"))
    url = "https://api.groupme.com/v3/groups/%s?token=%s" % group_id, os.getenv("ACCESS_TOKEN")
    send_message("2")
    request = Request(url)
    send_message("3")
    json = urlopen(request).read().decode()
    send_message("4")
    send_message(json)

