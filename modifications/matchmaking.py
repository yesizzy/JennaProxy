# don't even think about it star

from mitmproxy import http
from utils import defs


@defs.isFortniteAgent
def response(self, flow: http.HTTPFlow):
    url = flow.request.url
    method = flow.request.method

    if "/matchmakingservice/ticket/player/" in url and method == "GET":
        flow.response = http.Response.make(
            404, 
            b"", 
            {"Content-Type": "application/json"}
        )