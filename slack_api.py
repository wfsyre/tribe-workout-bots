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


def create_poll(channel_id, title, options, ts, anon):
    slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
    sc = SlackClient(slack_token)
    actions = []
    block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*" + title + "*"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Delete Poll",
                    "emoji": True
                },
                "value": str(ts),
                "action_id": "deletePoll:" + str(ts),
                "style": "danger"
            }
        },
        {
            "type": "divider"
        }
    ]
    for i in range(0, len(options)):
        block.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": options[i],
                "emoji": True,
                "link_names": True
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Vote",
                    "emoji": True
                },
                "value": str(ts),
                "action_id": "votePoll:" + str(i) + ":" + str(anon)
            }
        })
        block.append({
            "type": "divider"
        })

    block.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "DM me the current results",
                    "emoji": True
                },
                "action_id": "dmPoll:" + str(ts),
                "style": "primary"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Remind the slackers",
                    "emoji": True
                },
                "action_id": "remindPoll:" + str(ts),
                "style": "danger"
            }
        ]

    })
    print(block)
    sc.api_call("chat.postMessage", channel=channel_id, blocks=block)


def send_categories(title, channel_id, categories):
    slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
    sc = SlackClient(slack_token)
    block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*" + title + "*"
            }
        }
    ]
    for category in categories:
        if len(categories[category]) > 0:
            block.append({"type": "divider"})
            block.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*" + category + "*"
                }
            })
            names = ""
            for i in range(len(categories[category])):
                names += str(i + 1) + ") " + categories[category][i] + "\n"
            block.append({
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": names
                }
            })
        else:
            block.append({"type": "divider"})
            block.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*" + category + "*"
                }
            })
    print(block)
    sc.api_call("chat.postMessage", channel=channel_id, blocks=block)
