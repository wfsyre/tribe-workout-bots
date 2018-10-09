from database_connection import *
from utils import *
from slack_api import *
import random
from datetime import datetime

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
    BOT_CHANNEL = "CBJAJPZ8B"
    data = request.get_json()
    if 'text' in list(data['event'].keys()):
        lower_text = data['event']['text'].lower()
    if data['type'] == "url_verification":
        return jsonify({'challenge': data['challenge']})

    count = 0
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
        emojis = list(get_emojis()['emoji'].keys())
        numbers = random.sample(range(0, len(emojis)), 4)
        if emojis:
            yes = ":" + emojis[numbers[0]] + ":"
            drills = ":" + emojis[numbers[1]] + ":"
            injured = ":" + emojis[numbers[2]] + ":"
            no = ":" + emojis[numbers[3]] + ":"
        else:
            yes = ":yea:"
            drills = ":alienjeff:"
            no = ":nay:"
            injured = ":conni:"
        print(obj._calendar_title + " found with text "
              + obj._calendar_text + " with date "
              + obj._calendar_date.strftime("%B %d, %Y"))

        if add_reaction_info_date(obj._calendar_date, yes=yes, no=no, drills=drills, injured=injured):
            add_practice_date(obj._calendar_date.strftime("%Y-%m-%d"))
            send_calendar_message(
                obj._calendar_title + " " + obj._calendar_text.lower() + " on " + obj._calendar_date.strftime(
                    "%B %d, %Y") + "\n"
                + yes + " if you are playing \n"
                + drills + " if you are only doing drills\n"
                + injured + " if you are attending but not playing\n"
                + no + " if you are not attending")
        else:
            #send reminders
            unanswered = get_unanswered(obj._calendar_date.strftime("%Y-%m-%d"))
            string = ""
            unanswered = [x[0] for x in unanswered]
            for item in unanswered:
                string += "<@" + str(item) + ">\n"
            send_debug_message(string)
            for user_id in unanswered:
                im_data = open_im(user_id)
                if 'channel' in list(im_data.keys()):
                    channel = im_data['channel']['id']
                    send_message(
                        "<@" + user_id + "> please react to the message in announcements about practice attendance",
                        channel=channel,
                        bot_name="Reminder Bot")
                    send_debug_message(" Sent reminder to <@" + user_id + ">")
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
            if obj._event['text'][0:8] == 'Practice':
                # need to record timestamp of message here
                send_debug_message("Found practice reminder with timestamp %s" % obj._ts)
                if add_reaction_info_ts(obj._ts):
                    reactions = check_reaction_timestamp(obj._ts)
                    reactions = reactions[0]
                    date, yes, no, drills, injured, ts = reactions
                    reactions = [yes, no, drills, injured]
                    reactions = [x.strip(":") for x in reactions]
                    for reaction in reactions:
                        obj.like_message(reaction=reaction)

    print(obj)
    print("responding")
    return make_response("Ok", 200, )


class SlackResponse:
    # event
    # event_type
    # files = []
    # ts
    # text
    # channel
    # user_id
    # bot
    # mentions = []
    # points_to_add
    # all_ids
    # all_names
    def __init__(self, json_data):
        self._event = json_data['event']
        self._repeat = False
        self._reaction_added = False
        self._reaction_removed = False
        self._check_for_commands = False
        self._event_time = json_data['event_time']
        self._bot = 'bot_id' in list(self._event.keys()) and self._event['bot_id'] != None
        self._event_type = self._event['type']
        if 'files' in list(self._event.keys()):
            self._files = self._event['files']
        else:
            self._files = []
        if 'attachments' in list(self._event.keys()):
            self._calendar = True
            self._calendar_text = self._event['attachments'][0]['text']
            self._calendar_title = self._event['attachments'][0]['title']
            if self._calendar_title == 'Practice':
                date_text = self._calendar_text[self._calendar_text.index('|'):]
                date_text = date_text[1:date_text.index('from') - 1]
                # September 30th, 2018
                comma = date_text.index(",")
                date_text = date_text[0:comma - 2] + date_text[comma:]
                # September 30, 2018
                self._calendar_date = datetime.strptime(date_text, '%B %d, %Y')
        else:
            self._calendar = False
        if 'text' in list(self._event.keys()):
            self._text = self._event['text']
        else:
            self._text = ''

        self._subtype = self._event['subtype'] if 'subtype' in list(self._event.keys()) else 'message'
        if self._subtype == 'message_deleted':
            self._previous_message = self._event['previous_message']
            self._bot = True
            self._channel = self._event['channel']
            if self._channel != 'GBR6LQBMJ':
                send_debug_message("Found a deleted message in channel %s written by %s" % (
                self._channel, self._previous_message['user']))
                send_debug_message(self._previous_message['text'])
        elif self._subtype == 'message_changed':
            self._check_for_commands = True
            self._previous_message = self._event['previous_message']
            self._user_id = self._previous_message['user']
            self._previous_message_text = self._previous_message['text']
            self._text = self._event['message']['text']
            self._channel = self._event['channel']
            self._ts = self._event['message']['ts']
            send_debug_message("Found a edited message in channel %s that used to say:" % self._channel)
            send_debug_message(self._previous_message_text)
        elif self._subtype == 'bot_message':
            self._bot = True
            self._channel_type = self._event['channel_type']
            self._channel = self._event['channel']
            self._ts = self._event['ts']
            self.user_id = self._event['bot_id']
        elif self._event['type'] == 'reaction_added' or self._event['type'] == 'reaction_removed':
            self._reaction_added = self._event['type'] == 'reaction_added'
            if not self._bot:
                self._user_id = self._event['user']
            else:
                self.user_id = self._event['bot_id']
            self._reaction_removed = not self._reaction_added
            self._item = self._event['item']
            self._reaction = self._event['reaction']
            self._channel = self._item['channel']
            self._item_ts = self._item['ts']
            self._user_id = self._event['user']
        elif self._subtype == 'message' or self._subtype == 'file_share':
            self._check_for_commands = True
            self._bot = 'bot_id' in list(self._event.keys()) and self._event['bot_id'] != None or 'user' not in list(
                self._event.keys())
            self._event_type = self._event['type']
            self._ts = self._event['ts']
            self._channel = self._event['channel']
            self._channel_type = self._event['channel_type']
            if 'files' in list(self._event.keys()):
                self._files = self._event['files']
            else:
                self._files = []

            if 'text' in list(self._event.keys()):
                self._text = self._event['text']
            else:
                self._text = ''

            if not self._bot:
                self._user_id = self._event['user']
            else:
                self.user_id = self._event['bot_id'] if 'bot_id' in list(self._event.keys()) else ''

        if self._check_for_commands:
            self.parse_text_for_mentions()

            if not self._bot:
                self._all_ids = self._mentions + [self._user_id]
            else:
                self._all_ids = self._mentions

            self.match_names_to_ids()
            self._lower_text = self._text.lower()
            self.parse_for_additions()

    def parse_text_for_mentions(self):
        text = self._text
        indicies = []
        mention_ids = []
        i = 0
        while (i < len(text)):
            temp = text.find('@', i)
            if temp == -1:
                i = len(text)
            else:
                indicies.append(temp)
                i = temp + 1
        for index in indicies:
            mention_ids.append(text[index + 1:text.find('>', index)])
        self._mentions = mention_ids

    def match_names_to_ids(self):
        mention_ids = self._all_ids
        self._all_avatars = []
        mention_names = []
        info = get_group_info()
        for id in mention_ids:
            for member in info['members']:
                if member['id'] == id:
                    mention_names.append(member['real_name'])
                    self._all_avatars.append(member['profile']['image_512'])
        self._all_names = mention_names
        if len(self._all_names) > 0:
            self._name = self._all_names[-1]
            self._avatar_url = self._all_avatars[-1]
        else:
            self._name = ""

    def parse_for_additions(self):
        GYM_POINTS = 1.0
        TRACK_POINTS = 1.0
        THROW_POINTS = 0.5
        SWIM_POINTS = 1.0
        PICKUP_POINTS = 0.5
        BIKING_POINTS = 1.0
        self._points_to_add = 0
        if '!gym' in self._lower_text:
            self._points_to_add += GYM_POINTS
        if '!track' in self._lower_text:
            self._points_to_add += TRACK_POINTS
        if '!throw' in self._lower_text:
            self._points_to_add += THROW_POINTS
        if '!swim' in self._lower_text:
            self._points_to_add += SWIM_POINTS
        if '!pickup' in self._lower_text:
            self._points_to_add += PICKUP_POINTS
        if '!bike' in self._lower_text:
            self._points_to_add += BIKING_POINTS

    def handle_db(self):
        if not self._repeat:
            num = add_to_db(self._all_names, self._points_to_add, self._all_ids)
            if num == len(self._all_names):
                self.like_message()
            else:
                self.like_message(reaction='skull_and_crossbones')

    def isRepeat(self):
        self._repeat = add_num_posts([self._user_id], self._event_time, self._name)

    def execute_commands(self):
        count = 0
        if not self._repeat:
            if "!leaderboard" in self._lower_text:
                count += 1
                to_print = collect_stats(3, True)
                send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)
            if '!workouts' in self._lower_text:  # display the leaderboard for who works out the most
                count += 1
                to_print = collect_stats(2, True)
                send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)
            if '!talkative' in self._lower_text:  # displays the leaderboard for who posts the most
                count += 1
                to_print = collect_stats(1, True)
                send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)
            if '!handsome' in self._lower_text:  # displays the leaderboard for who posts the most
                count += 1
                to_print = collect_stats(1, True)
                send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)
            if '!heatcheck' in self._lower_text:
                count += 1
                send_tribe_message("Kenta wins", channel=self._channel)
            if '!regionals' in self._lower_text:
                count += 1
                now = datetime.now()
                regionals = datetime(2019, 4, 28, 8, 0, 0)
                until = regionals - now
                send_tribe_message("regionals is in " + stringFromSeconds(until.total_seconds()), channel=self._channel)
            if '!subtract' in self._lower_text and self._user_id == 'UAPHZ3SJZ':
                send_debug_message("SUBTRACTING: " + self._lower_text[-3:] + " FROM: " + str(self._all_names[:-1]))
                num = subtract_from_db(self._all_names[:-1], float(self._lower_text[-3:]), self._all_ids[:-1])
                count += 1
            if '!reset' in self._lower_text and self._user_id == 'UAPHZ3SJZ':
                to_print = collect_stats(3, True)
                send_tribe_message(to_print, channel=self._channel, bot_name=self._name)
                reset_scores()
                send_debug_message("Reseting leaderboard")
                count += 1
            if '!add' in self._lower_text and self._user_id == 'UAPHZ3SJZ':
                send_debug_message("ADDING: " + self._lower_text[-3:] + " TO: " + str(self._all_names[:-1]))
                num = add_to_db(self._all_names[:-1], self._lower_text[-3:], self._all_ids[:-1])
                count += 1
            if '!test' in self._lower_text:
                pass
            if '!remind' in self._lower_text:
                date = self._lower_text[-10:]
                unanswered = get_unanswered(date)
                unanswered = [x[0] for x in unanswered]
                for user_id in unanswered:
                    im_data = open_im(user_id)
                    if 'channel' in list(im_data.keys()):
                        channel = im_data['channel']['id']
                        send_message(
                            "<@" + user_id + "> please react to the message in announcements about practice attendance",
                            channel=channel,
                            bot_name="Reminder Bot")
                        send_debug_message(" Sent reminder to <@" + user_id + ">")
            if '!attendance' in self._lower_text:
                date = self._lower_text[-10:]
                attendance = get_practice_attendance(date)
                if 'failure' not in list(attendance.keys()):
                    send_tribe_message("practicing: " + str(attendance['playing']) + "\n"
                                       + "drills: " + str(attendance['drills']) + "\n"
                                       + "not playing: " + str(attendance['injured']) + "\n"
                                       + "not attending: " + str(attendance['missing']) + "\n"
                                       + "unanswered: " + str(attendance['unanswered']) + "\n",
                                       channel=self._channel,
                                       bot_name='Attendance Bot')
                else:
                    send_tribe_message("Either the date was improperly formatted or information on this date does not exist")
            if self._points_to_add > 0:
                self.like_message(reaction='angry')
            if 'groupme' in self._lower_text or 'bamasecs' in self._lower_text:
                self.like_message(reaction='thumbsdown')
            if 'good bot' in self._lower_text:
                self.like_message(reaction='woman-tipping-hand')
            if count >= 1:
                self.like_message(reaction='octopus')

    def like_message(self, reaction='robot_face'):
        slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
        sc = SlackClient(slack_token)
        res = sc.api_call("reactions.add", name=reaction, channel=self._channel, timestamp=self._ts)

    def __repr__(self):
        return str(self.__dict__)
