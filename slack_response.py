from database_connection import *
from utils import *
from slack_api import *
from datetime import datetime


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
        self.GYM_POINTS = 1.0
        self.TRACK_POINTS = 1.0
        self.THROW_POINTS = 0.5
        self.SWIM_POINTS = 1.0
        self.PICKUP_POINTS = 0.5
        self.BIKING_POINTS = 1.0
        self.RUN_POINTS = 1.0
        self.TOURNAMENT_POINTS = 2.0
        self._additions = []
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
            if 'practice' in self._calendar_title.lower():
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

        self._points_to_add = 0
        if '!gym' in self._lower_text:
            self._points_to_add += self.GYM_POINTS
            self._additions.append('!gym')
        if '!track' in self._lower_text:
            self._points_to_add += self.TRACK_POINTS
            self._additions.append('!track')
        if '!throw' in self._lower_text:
            self._points_to_add += self.THROW_POINTS
            self._additions.append('!throw')
        if '!swim' in self._lower_text:
            self._points_to_add += self.SWIM_POINTS
            self._additions.append('!swim')
        if '!pickup' in self._lower_text:
            self._points_to_add += self.PICKUP_POINTS
            self._additions.append('!pickup')
        if '!bike' in self._lower_text:
            self._points_to_add += self.BIKING_POINTS
            self._additions.append('!bike')
        if '!run' in self._lower_text:
            self._points_to_add += self.BIKING_POINTS
            self._additions.append('!run')
        if '!tournament' in self._lower_text:
            self._points_to_add += self.TOURNAMENT_POINTS
            self._additions.append('!tournament')

    def handle_db(self):
        if not self._repeat:
            num = add_to_db(self._all_names, self._points_to_add, len(self._additions), self._all_ids)
            for i in range(len(self._all_names)):
                for workout in self._additions:
                    add_workout(self._all_names[i], self._all_ids[i], workout)
            if num == len(self._all_names):
                self.like_message()
            else:
                self.like_message(reaction='skull_and_crossbones')

    def isRepeat(self):
        self._repeat = add_num_posts([self._user_id], self._event_time, self._name)

    def execute_commands(self):
        count = 0
        if not self._repeat:
            if "!help" in self._lower_text:
                send_tribe_message("Available commands:\n!leaderboard\n!workouts\n!talkative\n!regionals\n!points"
                                   "\n!gym\n!track\n!tournament\n!pickup\n!throw\n!swim\n!bike\n!run\n!since [YYYY-MM-DD] [type] [@name]"
                                   "\n!groupsince [YYYY-MM-DD] [type]"
                                   "\n!poll \"Title\" \"option 1\" ... \"option n\"",
                                   channel=self._channel, bot_name="Helper Bot")
            if "!points" in self._lower_text:
                send_tribe_message("Point Values:\ngym: %.1f\ntrack %.1f\ntournament %.1f\npickup %.1f\nthrow %.1f\nswim %.1f\nbike %.1f\nrun %.1f"
                                   % (self.GYM_POINTS, self.TRACK_POINTS, self.TOURNAMENT_POINTS, self.PICKUP_POINTS,
                                      self.THROW_POINTS, self.SWIM_POINTS, self.BIKING_POINTS, self.RUN_POINTS), channel=self._channel)
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
                print(num)
                count += 1
            if '!reset' in self._lower_text and self._user_id == 'UAPHZ3SJZ':
                to_print = collect_stats(3, True)
                send_tribe_message(to_print, channel=self._channel, bot_name=self._name)
                reset_scores()
                send_debug_message("Resetting leaderboard")
                count += 1
            if '!silence' in self._lower_text and self._user_id == 'UAPHZ3SJZ':
                to_print = collect_stats(1, True)
                send_tribe_message(to_print, channel=self._channel, bot_name=self._name)
                reset_talkative()
                send_debug_message("Resetting talkative")
                count += 1
            if '!add' in self._lower_text and self._user_id == 'UAPHZ3SJZ':
                send_debug_message("ADDING: " + self._lower_text[-3:] + " TO: " + str(self._all_names[:-1]))
                num = add_to_db(self._all_names[:-1], self._lower_text[-3:], 1, self._all_ids[:-1])
                print(num)
                count += 1
            if '!test' in self._lower_text:
                pass
            if '!clearpoll' in self._lower_text and self._user_id == 'UAPHZ3SJZ':
                clear_poll_data()
            if '!poll' in self._lower_text:
                #!poll "Title" "option 1" ... "option n"
                quotes = self._lower_text.count("\"")
                num_options = quotes - 2
                start = 0
                options = []
                while start < len(self._text):
                    first = self._text.find("\"", start)
                    if first == -1:
                        break
                    second = self._text.find("\"", first + 1)
                    options.append(self._text[first + 1:second])
                    start = second + 1
                im_data = open_im(self._user_id)
                channel = im_data['channel']['id']
                send_message(
                    "<@" + self._user_id + "> You made a tracked poll in channel " + self._channel
                    + " with tracking code",
                    channel=channel,
                    bot_name="Poll Helper")
                send_message(
                    "" + self._ts,
                    channel=channel,
                    bot_name="Poll Helper")
                anon = "anonymous" in self._lower_text[-10:]
                add_tracked_poll(options[0], self._user_id, self._ts, options[1:], self._channel, anon)
                add_poll_dummy_responses(self._ts)
                create_poll(self._channel, options[0], options[1:], self._ts, anon)
            if '!checkpoll' in self._lower_text:
                ts = self._lower_text[11:]
                title, data = get_poll_data(ts)
                send_categories(title, self._channel, data)
            if '!interpoll' in self._lower_text:
                ts = self._lower_text[11:]
                send_debug_message(ts)
                unanswered = get_poll_unanswered(ts)
                unanswered = [x[0] for x in unanswered]
                send_debug_message(unanswered)
                title, _ = get_poll_data(ts)
                for user_id in unanswered:
                    im_data = open_im(user_id)
                    if 'channel' in list(im_data.keys()):
                        channel = im_data['channel']['id']
                        send_message(
                            "<@" + user_id + "> Please react to the poll \"" + title + "\"",
                            channel=channel,
                            bot_name="Reminder Bot")
                        send_debug_message(" Sent reminder to <@" + user_id + ">")
            if '!remind' in self._lower_text:
                date = self._lower_text[-10:]
                send_debug_message("reminder batch being sent for " + date)
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
                    send_str = "practicing: " + str(attendance['playing']) + "\n"\
                               + "drills: " + str(attendance['drills']) + "\n"\
                               + "not playing: " + str(attendance['injured']) + "\n"\
                               + "not attending: " + str(attendance['missing']) + "\n"\
                               + "unanswered: " + str(attendance['unanswered']) + "\n"
                    send_str = send_str.replace("'", '')
                    send_tribe_message(send_str, channel=self._channel, bot_name='Attendance Bot')
                else:
                    send_tribe_message(
                        "Either the date was improperly formatted or information on this date does not exist",
                        channel=self._channel,
                        bot_name="Reminder Bot")
            if '!since' in self._lower_text:
                print("found !since")
                #!since YYYY-MM-DD type @name
                params = self._text.split(" ")
                print(params)
                workouts = get_workouts_after_date(params[1], params[2], params[3][2: -1])
                send_str = ""
                send_str += "%d total workouts found:\n" % (len(workouts))
                for workout in workouts:
                    print(workout)
                    send_str += "Name: %s, Workout Type: %s, Date: %s\n" % (workout[0], workout[2], workout[3].strftime("%-m/%d/%Y"))
                send_tribe_message(send_str, channel=self._channel)
            if '!groupsince' in self._lower_text:
                print("found !groupsince")
                #groupsince YYYY-MM-DD type
                params = self._text.split(" ")
                print(params)
                workouts = get_group_workouts_after_date(params[1], params[2])
                send_str = ""
                send_str += "%d total workouts found: \n" % (len(workouts))
                for workout in workouts:
                    print(workout)
                    send_str += "Name: %s, Workout Type: %s, Date: %s\n" % (workout[0], workout[2], workout[3].strftime("%-m/%d/%Y"))
                send_tribe_message(send_str, channel=self._channel)
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
