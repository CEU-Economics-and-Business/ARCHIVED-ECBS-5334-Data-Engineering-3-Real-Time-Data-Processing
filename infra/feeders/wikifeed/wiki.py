# pip install sseclient to get this working

import json
from datetime import datetime
from sseclient import SSEClient as EventSource

url = 'https://stream.wikimedia.org/v2/stream/recentchange'
for event in EventSource(url):
    if event.event == 'message':
        try:
            change = json.loads(event.data)
            if change["type"] not in ["edit", "new"]:
                continue
            ts = datetime.now()

            d = {
                "type": change["type"],
                "title": change["title"],
                "user": change["user"],
                "bot": change["bot"],
                "wiki": change["wiki"],
                "minor": change["minor"],
                "comment": change["comment"],
                "server_name": change["server_name"]
            }
        except (ValueError, KeyboardInterrupt):
            pass
        else:
            print(json.dumps(d))