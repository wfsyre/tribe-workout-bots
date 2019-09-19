from database_connection import *
from interactive_component_payload import InteractiveComponentPayload
from slack_response import SlackResponse
from slack_api import *
from time import sleep
import json

from flask import Flask, request, jsonify, make_response

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    print("event received")
    GYM_POINTS = 1.0
    TRACK_POINTS = 1.0
    THROW_POINTS = 0.5
    SWIM_POINTS = 1.0
    PICKUP_POINTS = 0.5
    BIKING_POINTS = 1.0
    RUN_POINTS = 1.0
    BOT_CHANNEL = "CBJAJPZ8B"
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
    if not obj._bot and not obj._reaction_added and not obj._reaction_removed:
        print("not a bot")
        obj.isRepeat()
        obj._repeat = False
        if obj._points_to_add > 0:
            print("points to add")
            obj.handle_db()
        else:
            print("executing commands")
            obj.execute_commands()
    elif obj._calendar:
        print("found a calendar reminder")
        # emojis = list(get_emojis()['emoji'].keys())
        # numbers = random.sample(range(0, len(emojis)), 4)
        # if emojis:
        #     yes = ":" + emojis[numbers[0]] + ":"
        #     drills = ":" + emojis[numbers[1]] + ":"
        #     injured = ":" + emojis[numbers[2]] + ":"
        #     no = ":" + emojis[numbers[3]] + ":"
        # else:
        #     yes = ":yea:"
        #     drills = ":alienjeff:"
        #     no = ":nay:"
        #     injured = ":conni:"
        yes = ":logan:"
        drills = ":youtried:"
        no = ":nay:"
        injured = ":nish:"
        print(obj._calendar_title + " found with text "
              + obj._calendar_text + " with date "
              + obj._calendar_date.strftime("%B %d, %Y"))

        if add_reaction_info_date(obj._calendar_date, yes=yes, no=no, drills=drills, injured=injured):
            add_dummy_responses(obj._calendar_date.strftime("%Y-%m-%d"))
            send_calendar_message(
                obj._calendar_title + " " + obj._calendar_text.lower() + " on " + obj._calendar_date.strftime(
                    "%B %d, %Y") + "\n"
                + yes + " if you are playing \n"
                + drills + " if you are only doing drills\n"
                + injured + " if you are attending but not playing\n"
                + no + " if you are not attending")
            create_calendar_poll(channel_id='#bot_testing',
                                 title=obj._calendar_title,
                                 date=obj._calendar_date.strftime("%Y-%m-%d"))
        else:
            # send reminders
            unanswered = get_unanswered(obj._calendar_date.strftime("%Y-%m-%d"))
            unanswered = [x[0] for x in unanswered]
            for user_id in unanswered:
                im_data = open_im(user_id)
                if 'channel' in list(im_data.keys()):
                    channel = im_data['channel']['id']
                    # send_message(
                    #     "<@" + user_id + "> please react to the message in announcements about practice attendance",
                    #     channel=channel,
                    #     bot_name="Reminder Bot")
                    send_debug_message(" Sent reminder to <@" + user_id + ">", level="DEBUG")
    elif obj._reaction_added:
        check = check_reaction_timestamp(obj._item_ts)
        if check:
            print(check)
            print(obj._user_id + " added a reaction :" + obj._reaction + ":")
            if obj._reaction == check[0][1].strip(":"):
                print("Found a yes")
                count_practice(obj._user_id, check[0][0].strftime("%Y-%m-%d"), 3)
            elif obj._reaction == check[0][2].strip(":"):
                print("Found a no")
                count_practice(obj._user_id, check[0][0].strftime("%Y-%m-%d"), 0)
            elif obj._reaction == check[0][3].strip(":"):
                print("Found a drills")
                count_practice(obj._user_id, check[0][0].strftime("%Y-%m-%d"), 2)
            elif obj._reaction == check[0][4].strip(":"):
                print("Found an injured")
                count_practice(obj._user_id, check[0][0].strftime("%Y-%m-%d"), 1)
            # need to update scores in tribe_attendance
        else:
            print("worthless reaction added by " + obj._user_id + " :" + obj._reaction + ":")
    elif obj._reaction_removed:
        check = check_reaction_timestamp(obj._item_ts)
        print(check)
        if check:
            count_practice(obj._user_id, check[0][0].strftime("%Y-%m-%d"), -1)
        else:
            print("worthless reaction added by " + obj._user_id + " :" + obj._reaction + ":")
        # need to update scores in tribe_attendance
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


@app.route('/poll', methods=['POST'])
def interactive_component_webhook():
    form_json = json.loads(request.form["payload"])
    print("This is the data that came with the interactive component")
    send_debug_message(str(form_json), level="INFO")
    return make_response("Ok", 200, )
