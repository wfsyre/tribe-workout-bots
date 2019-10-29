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
        self.GYM_POINTS = 0.5
        self.TRACK_POINTS = 0.5
        self.THROW_POINTS = 0.5
        self.SWIM_POINTS = 0
        self.PICKUP_POINTS = 0
        self.BIKING_POINTS = 0.5
        self.RUN_POINTS = 0.5
        self.TOURNAMENT_POINTS = 0
        self.WORKOUT_POINTS = 2.0
        self.CARDIO_POINTS = 0.5
        self._WORKOUT_TYPES = ["gym", "workout", "throw", "pickup", "cardio", "track"]
        self._WORKOUT_MAP = [(("!" + x), self[x.upper() + '_POINTS']) for x in self._WORKOUT_TYPES]
        send_debug_message(self._WORKOUT_MAP, level="DEBUG")
        self._COMMANDS = ["help", "since", "groupsince", "points",
                          "leaderboard", "workouts", "talkative",
                          "reset", "regionals", "subtract", "add",
                          "test", "poll"]
        self.CALENDAR_ENABLED = bool(os.getenv('ENABLE_CALENDAR'))
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
            self._calendar = True and self.CALENDAR_ENABLED
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
                self._channel, self._previous_message['user']), level="INFO")
                send_debug_message(self._previous_message['text'], level="INFO")
        elif self._subtype == 'message_changed':
            self._check_for_commands = True
            self._previous_message = self._event['previous_message']
            if 'user' in self._previous_message:
                self._user_id = self._previous_message['user']
            else:
                self._user_id = "BOT"
            self._previous_message_text = self._previous_message['text']
            self._text = self._event['message']['text']
            self._channel = self._event['channel']
            self._ts = self._event['message']['ts']
            if 'blocks' not in self._event['previous_message']:
                send_debug_message("Found a edited message in channel %s that used to say:" % self._channel, level="INFO")
                send_debug_message(self._previous_message_text, level="INFO")
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
            temp = text.find('<@', i)
            if temp == -1:
                i = len(text)
            else:
                indicies.append(temp)
                i = temp + 1
        for index in indicies:
            if text.find('>', index) != -1:
                mention_ids.append(text[index + 2:text.find('>', index)])
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
        for item in self._WORKOUT_MAP:
            if ("!" + item[0]) in self._lower_text:
                self._points_to_add += item[1]
                self._additions.append('!' + item[0])

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

    def add_num_posts(self):
        self._repeat = add_num_posts([self._user_id], self._event_time, self._name)

    def command_help(self):
        send_tribe_message("Available commands:\n!leaderboard\n!workouts\n!talkative\n!regionals\n!points"
                           "\n!gym\n!track\n!pickup\n!throw\n!cardio\nworkout"
                           "\n!since [YYYY-MM-DD] [type] [@name]"
                           "\n!groupsince [YYYY-MM-DD] [type]"
                           "\n!poll \"Title\" \"option 1\" ... \"option n\"",
                           channel=self._channel, bot_name="Helper Bot")

    def command_points(self):
        points_string = "Point Values\n"
        for points in self._WORKOUT_MAP:
            points_string += ("%s: %.1f\n" % (points[0], points[1]))

        send_tribe_message(points_string, channel=self._channel)

    def command_leaderboard(self):
        to_print = collect_stats(3, True)
        send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)

    def command_workouts(self):   # display the leaderboard for who works out the most
        to_print = collect_stats(2, True)
        send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)

    def command_talkative(self):  # displays the leaderboard for who posts the most
        to_print = collect_stats(1, True)
        send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)

    def command_handsome(self):   # displays the leaderboard for who posts the most
        to_print = collect_stats(1, True)
        send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)

    def admin_command_reteam(self):
        send_debug_message('re-teaming and excluding the tagged people from the leader board', level="DEBUG")
        reteam(self._mentions)

    def command_regionals(self):
        now = datetime.now()
        regionals = datetime(2020, 4, 28, 8, 0, 0)
        until = regionals - now
        send_tribe_message("regionals is in " + stringFromSeconds(until.total_seconds()), channel=self._channel)

    def admin_command_subtract(self):
        send_debug_message("SUBTRACTING: " + self._lower_text[-3:] + " FROM: " + str(self._all_names[:-1]),
                           level="INFO")
        subtract_from_db(self._all_names[:-1], float(self._lower_text[-3:]), self._all_ids[:-1])

    def admin_command_reset(self):
        to_print = collect_stats(3, True)
        send_tribe_message(to_print, channel=self._channel, bot_name=self._name)
        reset_scores()
        send_debug_message("Resetting leaderboard", level="INFO")

    def admin_command_add(self):
        send_debug_message("ADDING: " + self._lower_text[-3:] + " TO: " + str(self._all_names[:-1]), level="INFO")
        num = add_to_db(self._all_names[:-1], self._lower_text[-3:], 1, self._all_ids[:-1])

    def admin_command_test(self):
        pass

    def admin_command_clearpoll(self):
        clear_poll_data()

    def command_poll(self):
        # !poll "Title" "option 1" ... "option n"
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
        anon = "anonymous" in self._lower_text[-10:]
        add_tracked_poll(options[0], self._user_id, self._ts, options[1:], self._channel, anon)
        add_poll_dummy_responses(self._ts)
        send_debug_message(options, level="DEBUG")
        create_poll(self._channel, options[0], options[1:], self._ts, anon)

    def command_since(self):
        print("found !since")
        # !since YYYY-MM-DD type @name
        params = self._text.split(" ")
        print(params)
        workouts = get_workouts_after_date(params[1], params[2], params[3][2: -1])
        send_str = ""
        send_str += "%d total workouts found:\n" % (len(workouts))
        for workout in workouts:
            print(workout)
            send_str += "Name: %s, Workout Type: %s, Date: %s\n" % (
            workout[0], workout[2], workout[3].strftime("%-m/%d/%Y"))
        send_tribe_message(send_str, channel=self._channel)

    def command_groupsince(self):
        # groupsince YYYY-MM-DD type
        params = self._text.split(" ")
        print(params)
        workouts = get_group_workouts_after_date(params[1], params[2])
        send_str = ""
        send_str += "%d total workouts found: \n" % (len(workouts))
        for workout in workouts:
            print(workout)
            send_str += "Name: %s, Workout Type: %s, Date: %s\n" % (
            workout[0], workout[2], workout[3].strftime("%-m/%d/%Y"))
        send_tribe_message(send_str, channel=self._channel)

    def execute_commands(self):
        count = 0
        for command in self._COMMANDS:
            if ("!" + command) in self._lower_text:
                if "command_" + command in self.__dict__:
                    send_debug_message("Found command " + command, level="DEBUG")
                    # calls a method with the name scheme command_nameofcommand()
                    self["command_" + command]()
                    count += 1
                elif "admin_command_" + command in self.__dict__ and self._user_id in os.getenv("ADMIN_ID"):
                    send_debug_message("Found admin command " + command, level="DEBUG")
                    # calls a method with the name scheme admin_command_nameofcommand()
                    self["admin_command_" + command]()
                    count += 1
        # The rest of these are just for fun
        if self._points_to_add > 0:
            self.like_message(reaction='angry')
        if 'groupme' in self._lower_text or 'bamasecs' in self._lower_text:
            self.like_message(reaction='thumbsdown')
        if 'good bot' in self._lower_text:
            self.like_message(reaction='woman-tipping-hand')
        if count >= 1:
            # indicates a command was seen
            self.like_message(reaction='octopus')

    def like_message(self, reaction='robot_face'):
        slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
        sc = SlackClient(slack_token)
        res = sc.api_call("reactions.add", name=reaction, channel=self._channel, timestamp=self._ts)

    def __repr__(self):
        return str(self.__dict__)

    def __getitem__(self, item):
        return self.__dict__[item]
