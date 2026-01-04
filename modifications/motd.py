import json

from mitmproxy import http
from utils import defs


@defs.isFortniteAgent
def response(self, flow: http.HTTPFlow):
    url = flow.request.pretty_url
    method = flow.request.method

    if url.endswith("/api/v1/fortnite-br/channel/motd/target") and method == "POST":
        requestData = json.loads(flow.request.text)
        tags = requestData.get("tags", [])

        placements = []
        for i, tag in enumerate(tags):
            placements.append({
                "trackingId": "jennaproxy",
                "tag": tag,
                "locations": [],
                "position": 0
            })

        responseData = {
            "contentItems": [
                {
                    "contentHash": "jennaproxy",
                    "contentSchemaName": "DynamicMotd",
                    "contentFields": {
                        "fullScreenTitle": "JennaProxy",
                        "fullScreenBody": "Made by foxud & sizzy",
                        "teaserTitle": "JennaProxy",
                        "fullScreenBackground": {
                            "image": [
                                {
                                    "width": 1920,
                                    "height": 1080,
                                    "url": "https://cdn.foxud.dev/jennaproxy.png"
                                },
                                {
                                    "width": 960,
                                    "height": 540,
                                    "url": "https://cdn.foxud.dev/jennaproxy.png"
                                }
                            ],
                            "type": "FullScreenBackground"
                        },
                        "teaserBackground": {
                            "image": [
                                {
                                    "width": 720,
                                    "height": 400,
                                    "url": "https://cdn.foxud.dev/jennaproxy.png"
                                }
                            ],
                            "type": "TeaserBackground"
                        },
                        "verticalTextLayout": False
                    },
                    "placements": placements
                }
            ],
            "tcId": "jennaproxy"
        }

        flow.response.text = json.dumps(responseData)
        flow.response.headers["contentType"] = "application/json"