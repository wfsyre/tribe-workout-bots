from database_connection import *
from interactive_component_payload import InteractiveComponentPayload
from slack_response import SlackResponse
from slack_api import *
from time import sleep
import random
import json

from flask import Flask, request, jsonify, make_response, send_from_directory

app = Flask(__name__, static_folder='webapp/build')

# Serve React App
@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def serve(path):
    if path == 'api/data':
        return jsonify(select_all())
    if path == 'api/tournaments':
        return jsonify(tournaments())
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')



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
        if obj._subtype == 'message_changed' and obj._previous_message_text != obj._text and obj._channel == 'C019TQRH1DY':
            print("edited message to handle")
            obj.handle_edit()
        if obj._points_to_add > 0 and not obj._slackbot:
            print("points to add")
            obj.handle_db()
        elif obj._minutes_to_add > 0 and not obj._slackbot:
            print("minutes to add")
            obj.handle_db()
        else:
            print("executing commands")
            obj.execute_commands()

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
