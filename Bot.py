import os
import sys
import json
import ast
import urllib.request

from urllib.parse import urlencode
from urllib.request import Request, urlopen
url2 = "https://api.groupme.com/v3/groups/%s?token=%s" % ("35057943", "PcsqasJmWqUCp30dXjixH9Gm5AFDJ0DdqMPjeff5")
url = 'https://api.groupme.com/v3/bots/post'

data = {
    'attachments': [
        {
           'loci': [[15, 15], [31, 13]],
           'type': 'mentions',
           'user_ids': ['16388754', '15546365'],
       }
    ],
   'text': 'This is a test @Conor Brownell @Brandon Chen ',
    'bot_id': 'f748bac655b6f836eedbae14bb'
}
request = Request(url, urlencode(data).encode())
json = urlopen(request).read().decode()
