import os
import requests
from slackclient import SlackClient


def send_message(msg, channel="#bot_testing", url='', bot_name='Workout Bot'):
    slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
    sc = SlackClient(slack_token)
    if url == '':
        sc.api_call("chat.postMessage", channel=channel, text=msg, username=bot_name)
    else:
        sc.api_call("chat.postMessage", channel=channel, text=msg, username=bot_name, icon_url=url)


def send_debug_message(msg, bot_name='Workout Bot'):
    send_message(msg, channel="#bot_testing", bot_name=bot_name)


def send_tribe_message(msg, channel="#random", bot_name="Workout Bot"):
    send_message(msg, channel, bot_name=bot_name)


def send_calendar_message(msg):
    send_message(msg, channel="#announcements", bot_name='Reminder Bot')


def get_group_info():
    url = "https://slack.com/api/users.list?token=" + os.getenv('BOT_OATH_ACCESS_TOKEN')
    json = requests.get(url).json()
    return json


def get_emojis():
    url = 'https://slack.com/api/emoji.list?token=' + os.getenv('OATH_ACCESS_TOKEN')
    json = requests.get(url).json()
    return json


def open_im(user_id):
    url = "https://slack.com/api/im.open?token=" + os.getenv('BOT_OATH_ACCESS_TOKEN') + "&user=" + user_id
    json = requests.get(url).json()
    return json


def create_poll(channel_id, title, options, ts):
    slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
    sc = SlackClient(slack_token)
    actions = []
    for i in range(0, len(options)):
        actions.append({"type": "button", "text": {
            "type": "plain_text",
            "text": options[i],
            "emoji": True,
            "value": str([i, ts])
        }})

    block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": title
            }
        },
        {
            "type": "actions",
            "elements": actions
        }]
    print("\n\n\n\n\n")
    print(block)
    b = sc.api_call("chat.postMessage", channel=channel_id, blocks=block)
    print(b)
