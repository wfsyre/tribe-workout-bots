from database_connection import send_debug_message, add_poll_reaction, get_poll_owner,\
    get_poll_unanswered, get_poll_data, delete_poll
from slack_api import open_im, send_message, send_categories
from requests import post


class InteractiveComponentPayload:
    def __init__(self, json_data):
        self._slack_id = json_data['user']['id']
        self._action_id = json_data['actions'][0]["action_id"]
        self._actions = json_data['actions']
        self._json_data = json_data
        self._webhook_url = self._json_data['response_url']

    def handle_component(self):
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

    def vote_poll(self):
        ts = self._json_data['actions'][0]['value']
        colon = self._action_id.find(":")
        second_colon = self._action_id.find(":", colon + 1)
        response_num = self._action_id[colon + 1:second_colon]
        anon = bool(self._action_id[second_colon + 1:])
        send_debug_message("Found component interaction with id: " + self._slack_id
                           + ", ts: " + ts
                           + ", response_num: " + response_num)
        add_poll_reaction(ts, response_num, self._slack_id)
        if not anon:
            blocks = self._json_data['message']['blocks']
            current = blocks[2 * (int(response_num) + 1)]['text']['text']
            if self._slack_id not in current:
                blocks[2 * (int(response_num) + 1)]['text']['text'] = current + " <@" + self._slack_id + ">"
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
                "text": "Thanks for your response!",
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
                "Shame on <@" + self._slack_id + "> they tried to delete a poll they didn't own")

    def remind_poll(self):
        ts = self._action_id
        ts = ts[ts.find(":") + 1:]
        owner_id = get_poll_owner(ts)
        if len(owner_id) != 0 and owner_id in self._slack_id:
            unanswered = get_poll_unanswered(ts)
            unanswered = [x[0] for x in unanswered]
            print(unanswered)
            title, _ = get_poll_data(ts)
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
            send_debug_message("Shame on <@" + self._slack_id + "> they tried to send reminders for a poll they didn't own")

    def dm_poll(self):
        ts = self._action_id
        ts = ts[ts.find(":") + 1:]
        title, data = get_poll_data(ts)
        im_data = open_im(self._slack_id)
        if 'channel' in list(im_data.keys()):
            channel = im_data['channel']['id']
            send_categories(title, channel, data)
            send_debug_message(" Sent poll information to <@" + self._slack_id + ">")

    def vote_calendar(self):
        pass

