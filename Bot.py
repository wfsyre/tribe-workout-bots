import os
import sys
import json
import ast
import urllib.request

from urllib.parse import urlencode
from urllib.request import Request, urlopen
url2 = "https://api.groupme.com/v3/groups/%s?token=%s" % ("35057943", "PcsqasJmWqUCp30dXjixH9Gm5AFDJ0DdqMPjeff5")
url = 'https://api.groupme.com/v3/bots/post'

#data = {
#    'bot_id': 'f748bac655b6f836eedbae14bb',
#    "attachments": [
#       {
#              "loci": [
 #                [10, 13]
 #             ],
 #         "type": "mentions",
  #        "user_ids": ["16458398",]
   #     }
   #   ],
   # "text": "Attention @William Syre",
#}
data = {
  "bot_id": "f748bac655b6f836eedbae14bb",
  "text": "Text for @William Syre",
  "attachments": [
    {
      "type": "mentions",
      "user_ids": [16458398],
      "loci": [
        [9, 13]
      ]
    }
  ]
}
request = Request(url, urlencode(data).encode())
json = urlopen(request).read().decode()
