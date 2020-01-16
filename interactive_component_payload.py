from database_connection import *
from slack_api import *
from requests import post


class InteractiveComponentPayload:
    def __init__(self, json_data):
        self._json_data = json_data
        if 'callback_id' in self._json_data:  # for actions
            self._callback_id = self._json_data['callback_id']
            self._message = self._json_data['message']
            if 'user' in self._message:
                self._poster_id = self._message['user']
            else:
                self._poster_id = None
            self._actor = self._json_data['user']
            self._actor_id = self._actor['id']
            self._callback = True
        else:
            self._slack_id = json_data['user']['id']
            self._action_id = json_data['actions'][0]["action_id"]
            self._actions = json_data['actions']
            self._webhook_url = self._json_data['response_url']
            self._callback = False

    def handle_component(self):
        if self._callback:
            self.handle_action()
        else:
            self.parse_action_id(self._action_id)

    def parse_action_id(self, action_id):
        if "votePoll" in self._action_id:
            self.vote_poll()
        elif "deletePoll" in self._action_id:
            self.delete_poll()
        elif "dmPoll" in self._action_id:
            self.dm_poll()
        elif "remindPoll" in self._action_id:
            self.remind_poll()
        elif "voteCalendar" in self._action_id:
            self.vote_calendar()
        elif "remindCalendar" in self._action_id:
            self.remind_calendar()
        elif "deleteCalendar" in self._action_id:
            self.delete_calendar()
        elif "dmCalendar" in self._action_id:
            self.dm_calendar()

    def handle_action(self):
        if self._callback_id == 'banish':
            if self._poster_id is not None:
                im_data = open_im(self._poster_id)
                if 'channel' in list(im_data.keys()):
                    channel = im_data['channel']['id']
                    send_message(
                        "<@" + self._actor_id + "> has banished your message \""
                        + str(self._message['text'])
                        + "\" to the shadow realm!",
                        channel=channel,
                        bot_name="BANISH Bot")
                    react_message(reaction='no',
                                  timestamp=self._json_data['message_ts'],
                                  channel=self._json_data['channel']['id'])



    def vote_poll(self):
        ts = self._json_data['actions'][0]['value']
        colon = self._action_id.find(":")
        second_colon = self._action_id.find(":", colon + 1)
        response_num = self._action_id[colon + 1:second_colon]
        anon, multi, invisible = get_poll_settings(ts)
        real_name = get_user_info(self._slack_id)['user']['real_name']
        send_debug_message("Found component interaction with id: " + self._slack_id
                           + ", ts: " + ts
                           + ", response_num: " + response_num, level="DEBUG")
        result = add_poll_reaction(ts, response_num, self._slack_id, real_name)
        if result == -1:
            send_debug_message("Could not add <@" + self._slack_id + ">'s response to the poll")
            return
        blocks = self._json_data['message']['blocks']
        response_block = int(response_num) + 1
        current = blocks[response_block]['text']['text']
        if not anon:
            if multi:
                if self._slack_id not in current:
                    blocks[response_block]['text']['text'] = current + " <@" + self._slack_id + ">"
                else:
                    start = current.find(self._slack_id) - 2
                    end = start + 2 + len(self._slack_id) + 1
                    statement = current[0:start] + current[end + 1:]
                    blocks[response_block]['text']['text'] = statement
            else:
                poll_responses = get_poll_response(self._slack_id, ts)
                old_response_num = poll_responses[0][1]
                if old_response_num != -1:
                    # a response of 0 from the db lets us know this is a removal
                    old_response_block = int(old_response_num) + 1
                    old = blocks[old_response_block]['text']['text']
                    start = old.find(self._slack_id) - 2
                    end = start + 2 + len(self._slack_id) + 1
                    statement = old[0:start] + old[end + 1:]
                    blocks[old_response_block]['text']['text'] = statement
                if result == 1:
                    blocks[response_block]['text']['text'] = current + " <@" + self._slack_id + ">"
        else:
            if result == 0:
                blocks[response_block]['text']['text'] = current[:-12]
            elif result == 1:
                blocks[response_block]['text']['text'] = current + " :thumbsup: "

        if not invisible:
            slack_data = {
                "blocks": blocks,
                "replace_original": True,
            }
            post(
                self._webhook_url,
                json=slack_data,
                headers={'Content-Type': 'application/json'})
        else:
            slack_data = {
                "text": "Your vote has been recorded",
                "response_type": 'ephemeral',
                "replace_original": False
            }
            post(
                self._webhook_url,
                json=slack_data,
                headers={'Content-Type': 'application/json'})

    def delete_poll(self):
        ts = self._action_id
        ts = ts[ts.find(":") + 1:]
        owner_id = get_poll_owner(ts)
        print(owner_id)
        print(ts)
        if len(owner_id) != 0 and owner_id in self._slack_id:
            slack_data = {
                "delete_original": True
            }
            post(
                self._webhook_url,
                json=slack_data,
                headers={'Content-Type': 'application/json'})
            delete_poll(ts)
        elif len(owner_id) == 0:
            slack_data = {
                "delete_original": True
            }
            post(
                self._webhook_url,
                json=slack_data,
                headers={'Content-Type': 'application/json'})
        else:
            slack_data = {
                "text": "Nice try, but you must be the owner of the poll to delete it. Try making a poll of your own!",
                "response_type": 'ephemeral',
                "replace_original": False
            }
            post(
                self._webhook_url,
                json=slack_data,
                headers={'Content-Type': 'application/json'})
            send_debug_message(
                "Shame on <@" + self._slack_id + "> they tried to delete a poll they didn't own", level="DEBUG")

    def remind_poll(self):
        ts = self._action_id
        ts = ts[ts.find(":") + 1:]
        owner_id = get_poll_owner(ts)
        if len(owner_id) != 0 and owner_id in self._slack_id:
            unanswered = get_poll_unanswered(ts)
            unanswered = [x[0] for x in unanswered]
            print(unanswered)
            title, _data, _anon = get_poll_data(ts)
            for user_id in unanswered:
                im_data = open_im(user_id)
                if 'channel' in list(im_data.keys()):
                    channel = im_data['channel']['id']
                    send_message(
                        "<@" + user_id + "> Please react to the poll \"" + title + "\"",
                        channel=channel,
                        bot_name="Reminder Bot")
            slack_data = {
                "text": "Sent reminders to " + str(len(unanswered)) + " people",
                "response_type": 'ephemeral',
                "replace_original": False
            }
            post(
                self._webhook_url,
                json=slack_data,
                headers={'Content-Type': 'application/json'})
        elif len(owner_id) == 0:
            slack_data = {
                "delete_original": True
            }
            post(
                self._webhook_url,
                json=slack_data,
                headers={'Content-Type': 'application/json'})
        else:
            slack_data = {
                "text": "Nice try, but you must be the owner of the poll to spam reminders",
                "response_type": 'ephemeral',
                "replace_original": False
            }
            post(
                self._webhook_url,
                json=slack_data,
                headers={'Content-Type': 'application/json'})
            send_debug_message("Shame on <@" + self._slack_id + "> they tried to send reminders for a poll they didn't own", level="DEBUG")

    def dm_poll(self):
        dm_data = self._action_id
        first = dm_data.find(":")
        ts = dm_data[first + 1:]
        title, data, anon = get_poll_data(ts)
        anon, multi, invisible = get_poll_settings(ts)

        im_data = open_im(self._slack_id)
        if 'channel' in list(im_data.keys()):
            channel = im_data['channel']['id']
            if not invisible:
                send_categories(title, channel, data)
                send_debug_message("Sent poll information to <@" + self._slack_id + ">", level="DEBUG")
            else:
                send_message("You thought you could just press the button and get the results, huh?", channel, bot_name="SHAME")
                send_debug_message("Sent shame information to <@" + self._slack_id + ">", level="DEBUG")

    def vote_calendar(self):
        date = self._json_data['actions'][0]['value']
        vote_data = self._action_id
        first = vote_data.find(":")
        number = vote_data[first + 1:]
        count_practice(self._slack_id, date, number)
        send_debug_message("Practice counted for <@" + str(self._slack_id) + "> as " + str(number), level="DEBUG")
        blocks = self._json_data['message']['blocks']
        response_block = 2 * (int(number) + 1)
        current = blocks[response_block]['text']['text']
        if self._slack_id not in current:
            blocks[response_block]['text']['text'] = current + " <@" + self._slack_id + ">"
        else:
            start = current.find(self._slack_id) - 2
            end = start + 2 + len(self._slack_id) + 1
            statement = current[0:start] + current[end + 1:]
            blocks[response_block]['text']['text'] = statement

        slack_data = {
            "blocks": blocks,
            "replace_original": True,
        }
        post(
            self._webhook_url,
            json=slack_data,
            headers={'Content-Type': 'application/json'})

    def dm_calendar(self):
        dm_data = self._action_id
        first = dm_data.find(":")
        date = dm_data[first + 1:]
        categories = get_practice_attendance(date)
        im_data = open_im(self._slack_id)
        if 'channel' in list(im_data.keys()):
            channel = im_data['channel']['id']
            send_categories("Attendance for " + str(date), channel, categories)
            send_debug_message(" Sent calendar information to <@" + self._slack_id + ">", level="DEBUG")

    def delete_calendar(self):
        if self._slack_id == os.getenv("ADMIN_ID"):
            send_debug_message("Delete calendar pressed", level="DEBUG")
            dm_data = self._action_id
            first = dm_data.find(":")
            date = dm_data[first + 1:]
            slack_data = {
                "delete_original": True
            }
            post(
                self._webhook_url,
                json=slack_data,
                headers={'Content-Type': 'application/json'})
            delete_calendar(date)
        else:
            send_debug_message("<@" + self._slack_id + "> tried to delete a calendar post", level="DEBUG")

    def remind_calendar(self):
        if self._slack_id == os.getenv("ADMIN_ID"):    # That's me :)
            dm_data = self._action_id
            first = dm_data.find(":")
            date = dm_data[first + 1:]
            unanswered = get_unanswered(date)
            unanswered = [x[0] for x in unanswered]
            for slacker in unanswered:
                im_data = open_im(slacker)
                if 'channel' in list(im_data.keys()):
                    channel = im_data['channel']['id']
                    send_message(bot_name="Reminder Bot", msg="Please respond to the practice poll for " + str(date), channel=channel)
                    send_debug_message(" Sent poll information to <@" + self._slack_id + ">", level="DEBUG")
        else:
            send_debug_message("<@" + self._slack_id + "> tried to remind a calendar post", level="DEBUG")



