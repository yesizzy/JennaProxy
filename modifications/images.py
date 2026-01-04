from mitmproxy import http
from utils import defs


@defs.isFortniteAgent
def request(self, flow: http.HTTPFlow):
    url = flow.request.url

    if url.endswith(".png") or url.endswith(".jpg") or url.endswith(".jpeg"):
        flow.request.url = "https://cdn.foxud.dev/jennaproxy.png"