from database_connection import *
from interactive_component_payload import InteractiveComponentPayload
from slack_response import SlackResponse
from slack_api import *
from time import sleep
import random
import json

from flask import Flask, request, jsonify, make_response

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    print("event received")
    data = request.get_json()
    if data['type'] == "url_verification":
        return jsonify({'challenge': data['challenge']})
    print('HTTP_X_SLACK_RETRY_NUM' in list(request.__dict__['environ'].keys()))
    if 'HTTP_X_SLACK_RETRY_NUM' in list(request.__dict__['environ'].keys()):
        print("Retry Number " + request.__dict__['environ']['HTTP_X_SLACK_RETRY_NUM'])
        if int(request.__dict__['environ']['HTTP_X_SLACK_RETRY_NUM']):
            return make_response("Ok", 200, )
    print(data)
    obj = SlackResponse(data)
    if (not obj._bot or obj._slackbot) and not obj._reaction_added and not obj._reaction_removed:
        obj.add_num_posts()
        if obj._points_to_add > 0 and not obj._slackbot:
            print("points to add")
            obj.handle_db()
        else:
            print("executing commands")
            obj.execute_commands()
    else:
        if 'username' in list(obj._event.keys()) and obj._event['username'] == 'Reminder Bot':
            send_debug_message(str(obj), level="DEBUG")
            if 'practice' in obj._event['text'].lower():
                # need to record timestamp of message here
                send_debug_message("Found practice reminder with timestamp %s" % obj._ts, level="DEBUG")
                if add_reaction_info_ts(obj._ts):
                    reactions = check_reaction_timestamp(obj._ts)
                    reactions = reactions[0]
                    date, yes, no, drills, injured, ts = reactions
                    reactions = [yes, drills, injured, no]
                    reactions = [x.strip(":") for x in reactions]
                    for reaction in reactions:
                        obj.like_message(reaction=reaction)
                        sleep(.5)

    print(obj)
    print("responding")
    return make_response("Ok", 200, )


@app.route('/interactiveComponents', methods=['POST'])
def interactive_component_webhook():
    form_json = json.loads(request.form["payload"])
    print("This is the data that came with the interactive component")
    print(form_json)
    obj = InteractiveComponentPayload(form_json)
    obj.handle_component()
    return make_response("Ok", 200, )
