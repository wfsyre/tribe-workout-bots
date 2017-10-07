import os
import sys
import json
import ast
import urllib.request

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log('Recieved {}'.format(data))
    send_message(data)

    # We don't want to reply to ourselves!
    if data['name'] != 'TEST':
        #msg = '{}, you sent "{}".'.format(data['name'], data['text'])
        #send_message(msg)
        if len(data['attachments']) > 0:
            group_members = get_group_info(data['group_id'])
            names = []
            for attachment in data["attachments"]:
                if attachment['type'] == 'image':
                    send_image(attachment['url'])
                if attachment['type'] == 'mentions':
                    for mentioned in attachment['user_ids']:
                        for member in group_members:
                            if member["user_id"] == mentioned:
                                names.append(member["nickname"])
    return "ok", 200


def send_message(msg):
    url = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': msg,
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()

def send_image(img_url):

    url = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': "YOUR IMAGES ARE MINE NOW",
        'attachments': [
            {
                'type': 'image',
                'url': img_url
            }
        ]
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()

def log(msg):
    print(str(msg))
    sys.stdout.flush()

def get_group_info(group_id):
    with urllib.request.urlopen("https://api.groupme.com/v3/groups/%s?token=%s" % (group_id, os.getenv("ACCESS_TOKEN"))) as response:
        html = response.read()
    url = "https://api.groupme.com/v3/groups/%s?token=%s" % (group_id, os.getenv("ACCESS_TOKEN"))
    dict = parse_group_for_members(html)
    return dict["response"]["members"]

def parse_group_for_members(html_string):
    return json.loads(html_string)


