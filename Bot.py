import urllib.request
import ast
import json
url = "https://api.groupme.com/v3/groups/%s?token=%s" % ("35057943", "PcsqasJmWqUCp30dXjixH9Gm5AFDJ0DdqMPjeff5")
with urllib.request.urlopen(url) as response:
    html = response.read()
print(json.loads(html)["response"]["members"])
