from database_connection import *
from utils import *
from slack_api import *
from datetime import datetime, timedelta
from pytz import timezone


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

        # Parse the instance variables for point values
        self._WORKOUT_TYPES = ["gym", "workout", "throw", "cardio"]
        self._WORKOUT_TUPLES = [(("!" + x), self[x.upper() + '_POINTS']) for x in self._WORKOUT_TYPES]
        self._WORKOUT_MAP = {"!" + x: self[x.upper() + '_POINTS'] for x in self._WORKOUT_TYPES}

        # Parse the Slack response object for methods that should be turned into runnable commands for the bot
        self._COMMANDS = [x for x in dir(self) if "command_" in x and callable(getattr(self, x))]

        self.CALENDAR_ENABLED = bool(os.getenv('ENABLE_CALENDAR'))

        # instantiate some dummy variables
        self._additions = []
        self._reaction_added = False
        self._reaction_removed = False
        self._check_for_commands = False
        self._event_time = json_data['event_time']
        self._bot = 'bot_id' in self._event and self._event['bot_id'] != None

        # to allow slackbot to run some commands
        self._slackbot = 'user' in self._event and self._event['user'] == 'USLACKBOT'

        self._event_type = self._event['type']
        self._calendar = False
        if 'files' in list(self._event.keys()):
            self._files = self._event['files']
        else:
            self._files = []
        if 'text' in list(self._event.keys()):
            self._text = self._event['text']
        else:
            self._text = ''
        self._subtype = self._event['subtype'] if 'subtype' in list(self._event.keys()) else 'message'
        if self._subtype == 'message_deleted':
            self._previous_message = self._event['previous_message']
            self._bot = True
            self._channel = self._event['channel']
            if self._channel not in 'GPA9BE3DL':
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
                send_debug_message("Found a edited message in channel %s that used to say:" % self._channel,
                                   level="INFO")
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

            if 'user' in self._event:
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
        for item in self._WORKOUT_TUPLES:
            if item[0] in self._lower_text:
                self._points_to_add += item[1]
                self._additions.append(item[0])

    def handle_db(self):
        print("handling db")
        num = add_to_db(self._all_names, self._points_to_add, len(self._additions), self._all_ids)
        for i in range(len(self._all_names)):
            for workout in self._additions:
                add_workout(self._all_names[i], self._all_ids[i], workout)
        if num == len(self._all_names):
            self.like_message()
        else:
            self.like_message(reaction='skull_and_crossbones')

    def add_num_posts(self):
        add_num_posts([self._user_id], self._name)

    def command_help(self):
        send_tribe_message("Available commands:\n!leaderboard\n!workouts\n!talkative\n!regionals\n!points"
                           "\n!gym\n!throw\n!cardio\n!workout"
                           "\n!since [YYYY-MM-DD] [type] [@name]"
                           "\n!groupsince [YYYY-MM-DD] [type]"
                           "\n!poll \"Title\" \"option 1\" ... \"option n\""
                           "\n!daygraph [workout_type]",
                           channel=self._channel, bot_name="Helper Bot")

    def command_points(self):
        points_string = "Point Values\n"
        for points in self._WORKOUT_TUPLES:
            points_string += ("%s: %.1f\n" % (points[0], points[1]))

        send_tribe_message(points_string, channel=self._channel)

    def command_leaderboard(self):
        to_print = collect_stats(3, True)
        send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)

    def command_workouts(self):  # display the leaderboard for who works out the most
        to_print = collect_stats(2, True)
        send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)

    def command_talkative(self):  # displays the leaderboard for who posts the most
        to_print = collect_stats(1, True)
        send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)

    def command_handsome(self):  # displays the leaderboard for who posts the most
        to_print = collect_stats(1, True)
        send_message(to_print, channel=self._channel, bot_name=self._name, url=self._avatar_url)

    def command_regionals(self):
        now = datetime.now()
        if (now.month >= 5 and now.day >= 5) or now.month >= 6:
            regionals = datetime(now.year + 1, 4, 28, 8, 0, 0)
        else:
            regionals = datetime(now.year, 4, 28, 8, 0, 0)
        until = regionals - now
        send_tribe_message("regionals is in " + stringFromSeconds(until.total_seconds()), channel=self._channel)

    def command_poll(self):
        # !poll "Title" "option 1" ... "option n"
        self._text = self._text.replace("“", "\"")  # Get rid of "smart quotes"
        self._text = self._text.replace("”", "\"")  # Get rid of "smart quotes"
        self._text = self._text.replace("\'", "\"")  # Get rid of other quote options
        start = 0
        options = []
        while start < len(self._text):
            first = self._text.find("\"", start)
            if first == -1:
                break
            second = self._text.find("\"", first + 1)
            options.append(self._text[first + 1:second])
            start = second + 1
        if len(options) < 2:
            send_tribe_message("Incorrect poll command formatting, should be:"
                               "\n!poll \"Title\" \"Option 1\" ... \"Option n\"")
        else:
            anon = "anonymous" in self._lower_text[-10:]
            add_tracked_poll(options[0], self._user_id, self._ts, options[1:], self._channel, anon)
            add_poll_dummy_responses(self._ts)
            send_debug_message(options, level="DEBUG")
            create_poll(self._channel, options[0], options[1:], self._ts, anon)

    def command_singlepoll(self):
        # !poll "Title" "option 1" ... "option n"
        self._text = self._text.replace("“", "\"")  # Get rid of "smart quotes"
        self._text = self._text.replace("”", "\"")  # Get rid of "smart quotes"
        self._text = self._text.replace("\'", "\"")  # Get rid of other quote options
        start = 0
        options = []
        while start < len(self._text):
            first = self._text.find("\"", start)
            if first == -1:
                break
            second = self._text.find("\"", first + 1)
            options.append(self._text[first + 1:second])
            start = second + 1
        if len(options) < 2:
            send_message("Incorrect poll command formatting, should be:"
                               "\n!poll \"Title\" \"Option 1\" ... \"Option n\"", channel=self._channel)
        else:
            anon = "anonymous" in self._lower_text[-10:]
            add_tracked_poll(options[0], self._user_id, self._ts, options[1:], self._channel, anon, multi=False)
            add_poll_dummy_responses(self._ts)
            send_debug_message(options, level="DEBUG")
            create_poll(self._channel, options[0], options[1:], self._ts, anon)

    def command_since(self):
        # !since YYYY-MM-DD type @name
        params = self._text.split(" ")
        workouts = get_workouts_after_date(params[1], params[2], params[3][2: -1])
        send_str = ""
        send_str += "%d total workouts found:\n" % (len(workouts))
        for workout in workouts:
            send_str += "Name: %s, Workout Type: %s, Date: %s\n" % (
                workout[0], workout[2], workout[3].strftime("%-m/%d/%Y"))
        send_tribe_message(send_str, channel=self._channel)

    def command_groupsince(self):
        # groupsince YYYY-MM-DD type
        params = self._text.split(" ")
        workouts = get_group_workouts_after_date(params[1], params[2])
        # scrub subtractions and additions
        workouts = [[name, slack_id, workout_type, date] for (name, slack_id, workout_type, date) in workouts if
                    "!" in workout_type]
        send_str = "%d total workouts found: \n" % (len(workouts))
        for workout in workouts:
            send_str += "Name: %s, Workout Type: %s, Date: %s\n" % (
                workout[0], workout[2], workout[3].strftime("%-m/%d/%Y"))
        send_tribe_message(send_str, channel=self._channel)

    def command_trending(self):
        some_days_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        workouts = get_group_workouts_after_date(some_days_ago, "all")
        people_counts = {}
        for name, slack_id, workout_type, date in workouts:
            if "!" not in workout_type:  # found a subtraction or addition
                people_counts[name] = people_counts.setdefault(name, 0) + float(workout_type)
            else:
                people_counts[name] = people_counts.setdefault(name, 0) + self._WORKOUT_MAP[workout_type]
        file_name = generate_trending_bargraph(people_counts)
        send_file(file_name, self._channel)

    def command_daygraph(self):
        action = self._lower_text.split(" ")[1]
        workouts = get_group_workouts_after_date(None, action)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_counts = {x: 0 for x in days}
        for name, slack_id, type, date in workouts:
            day_of_the_week = date.strftime("%a")
            day_counts[day_of_the_week] += 1

        file_name = generate_bargraph(labels=days,
                                      values=[day_counts[x] for x in days],
                                      title="When does Tribe %s?" % action,
                                      x_label="Day of the Week",
                                      y_label="Number of " + action)
        send_file(file_name, self._channel)

    def command_feedback(self):
        now = datetime.now(tz=timezone('US/Eastern'))
        title = "How would you rate Tribe's EFFORT at tonight's practice" + now.strftime("%m/%d/%Y")
        options = ["Excellent (Sustained stretches competing at tournament levels",
                   "Good (Moments competing at tournament levels",
                   "Average (OK effort, but we did not push ourselves",
                   "Low"]
        anonymous = True
        add_tracked_poll(title, os.getenv("ADMIN_ID"), self._ts, options, self._channel, anonymous, multi=False, invisible=True)
        add_poll_dummy_responses(self._ts)
        create_poll(self._channel, title, options, self._ts, anonymous)
        register_feedback_poll(self._ts)


    def admin_command_setup(self):
        send_debug_message('Setting up new database', level="INFO")
        setup()
        send_debug_message('Database setup successful', level="INFO")

    def admin_command_reteam(self):
        send_debug_message('re-teaming and excluding the tagged people from the leaderboard', level="INFO")
        reteam(self._mentions)

    def admin_command_subtract(self):
        # !subtract @name1 @name2 ... 2.5
        people_to_subtract = self._all_names[:-1]
        subtraction = self._lower_text[-3:]
        try:
            subtraction = float(subtraction)
            send_debug_message("SUBTRACTING: " + str(subtraction) + " FROM: " + str(people_to_subtract), level="INFO")
            num = subtract_from_db(self._all_names[:-1], self._lower_text[-3:], self._all_ids[:-1])
            for name, id in zip(self._all_names[:-1], self._all_ids[:-1]):
                add_workout(name, id, "-" + str(subtraction))
        except:
            send_debug_message("Invalid subtraction value. Must be a float of the form X.X", level="ERROR")

    def admin_command_reset(self):
        to_print = collect_stats(3, True)
        send_tribe_message(to_print, channel=self._channel, bot_name=self._name)
        reset_scores()
        send_debug_message("Resetting leaderboard", level="INFO")

    def admin_command_add(self):
        # !add @name1 @name2 ... 2.5
        people_to_add = self._all_names[:-1]
        addition = self._lower_text[-3:]
        try:
            addition = float(addition)
            send_debug_message("ADDING: " + str(addition) + " TO: " + str(people_to_add), level="INFO")
            num = add_to_db(self._all_names[:-1], self._lower_text[-3:], 1, self._all_ids[:-1])
            for name, id in zip(self._all_names[:-1], self._all_ids[:-1]):
                add_workout(name, id, str(addition))
        except:
            send_debug_message("Invalid addition value. Must be a float of the form X.X", level="ERROR")

    def admin_command_test(self):
        send_debug_message("Found a test message", level='INFO')

    def admin_command_yaml(self):
        custom_emoji_file = open("custom_emoji_names.yaml", "w")
        emoji_json = get_emojis()['emoji']
        custom_emoji_file.write("title: custom\nemojis:\n")
        for b in emoji_json.keys():
            custom_emoji_file.write("  - name: " + b)
            custom_emoji_file.write("\n    src: \"" + emoji_json[b] + "\"\n")
        custom_emoji_file.close()
        send_file('custom_emoji_names.yaml', self._channel)

    def admin_command_clearpoll(self):
        clear_poll_data()

    def admin_command_recount(self):
        params = self._text.split(" ")
        since_date = params[1]
        workouts = get_group_workouts_after_date(since_date, 'all')
        leaderboard = {}
        for name, slack_id, type, time in workouts:
            if type not in self._WORKOUT_MAP:  # additions and subtractions are not in the workout map and must be handled differently
                if slack_id in leaderboard:
                    leaderboard[slack_id] += float(type)
                else:
                    leaderboard[slack_id] = float(type)
            else:
                if slack_id in leaderboard:
                    leaderboard[slack_id] += self._WORKOUT_MAP[type]
                else:
                    leaderboard[slack_id] = self._WORKOUT_MAP[type]
        set_leaderboard_from_dict(leaderboard)
        self.command_leaderboard()

    def execute_commands(self):
        count = 0
        for command in self._COMMANDS:
            index = command.find("command_") + 8
            if ("!" + command[index:]) in self._lower_text and 'admin' not in command:
                if command in dir(self):
                    # calls a method with the name scheme command_nameofcommand()
                    getattr(self, command)()
                    count += 1
            elif ("!" + command[index:]) in self._lower_text:
                if command in dir(self) and self._user_id in os.getenv("ADMIN_ID"):
                    # calls a method with the name scheme admin_command_nameofcommand()
                    getattr(self, command)()
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
