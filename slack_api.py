import os
import requests
from slackclient import SlackClient

verbosity = 1   # info lvl


def send_message(msg, channel="#bot_testing", url='', bot_name='Workout Bot'):
    slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
    sc = SlackClient(slack_token)
    if url == '':
        sc.api_call("chat.postMessage", channel=channel, text=msg, username=bot_name)
    else:
        sc.api_call("chat.postMessage", channel=channel, text=msg, username=bot_name, icon_url=url)


def react_message(channel, timestamp, reaction='robot_face'):
    slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
    sc = SlackClient(slack_token)
    res = sc.api_call("reactions.add", name=reaction, channel=channel, timestamp=timestamp)


def send_debug_message(msg, bot_name='Workout Bot', level="ERROR"):
    lvl = 0
    string = "DEBUG"
    if level == "ERROR":
        string = "<@" + os.getenv("ADMIN_ID") + "> ERROR:"
        lvl = 2
    elif level == "INFO":
        string = "INFO:"
        lvl = 1
    else:
        string = "DEBUG:"
        lvl = 0

    if lvl >= verbosity:
        send_message(string + str(msg), channel="#bot_testing", bot_name=bot_name)
    else:
        print(string, msg)


def send_tribe_message(msg, channel="#general", bot_name="Workout Bot"):
    send_message(msg, channel, bot_name=bot_name)


def send_calendar_message(msg):
    send_message(msg, channel="#announcements", bot_name='Reminder Bot')


def get_group_info():
    url = "https://slack.com/api/users.list?token=" + os.getenv('BOT_OATH_ACCESS_TOKEN')
    json = requests.get(url).json()
    return json

def get_user_info(slack_id):
    url = "https://slack.com/api/users.info?token=" + os.getenv('BOT_OATH_ACCESS_TOKEN') + "&user=" + slack_id
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
                "text": options[i]
            }
        })
        print("votePoll:" + str(i) + ":" + str(anon))
        actions.append(
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": options[i],
                    "emoji": True
                },
                "value": str(ts),
                "action_id": "votePoll:" + str(i) + ":" + str(anon)
            }
        )
    block.append({
        "type": "actions",
        "elements": actions
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
                names += str(i + 1) + ") " + str(categories[category][i]) + "\n"
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


def create_calendar_poll(channel_id, title, date):
    slack_token = os.getenv('BOT_OATH_ACCESS_TOKEN')
    options = ['Absent', 'Not playing but present', 'Drills only', 'Playing']
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
                    "text": "Delete Practice",
                    "emoji": True
                },
                "value": str(date),
                "action_id": "deleteCalendar:" + str(date),
                "style": "danger"
            }
        },
        {
            "type": "divider"
        }
    ]
    elem = []
    for i in range(0, len(options)):
        elem.append({
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": options[i],
                "emoji": True
            },
            "value": str(date),
            "action_id": "voteCalendar:" + str(i)
        })
    block.append({
        "type": "actions",
        "elements": elem
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
                    "text": "DM me the current attendance",
                    "emoji": True
                },
                "action_id": "dmCalendar:" + str(date),
                "style": "primary"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Remind the slackers",
                    "emoji": True
                },
                "action_id": "remindCalendar:" + str(date),
                "style": "danger"
            }
        ]

    })
    sc.api_call("chat.postMessage", channel=channel_id, blocks=block)
