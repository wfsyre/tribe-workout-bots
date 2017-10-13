import os
import sys
import json
import ast
import urllib.request

from urllib.parse import urlencode
from urllib.request import Request, urlopen
url2 = "https://api.groupme.com/v3/groups/%s?token=%s" % ("35057943", "PcsqasJmWqUCp30dXjixH9Gm5AFDJ0DdqMPjeff5")
url = 'https://api.groupme.com/v3/bots/post'

def like_workout_photo(conversation_id, message_id):
    url = 'https://api.groupme.com/v3/bots/post/messages'
    data = {
        'conversation_id' : conversation_id,
        'message_id' : message_id
    }
    request = Request(url, urlencode(data).encode())
    request.
    json = urlopen(request"/like").read().decode()