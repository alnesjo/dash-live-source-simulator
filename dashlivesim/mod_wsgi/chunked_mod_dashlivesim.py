from dashlivesim import SERVER_AGENT
from os.path import splitext
from time import time
from dashlivesim.dashlib import dash_proxy


def get_mime_type(ext):
    "Get mime-type depending on extension."
    if ext == '.mpd':
        return 'application/dash+xml'
    elif ext == '.m4s':
        return 'video/iso.segment'
    elif ext == '.mp4':
        return 'video/mp4'
    else:
        return 'text/plain'


def application(environment, start_response):
    path_parts = environment['REQUEST_URI'].split('/')
    start_response('200 OK', [('Content-Type', get_mime_type(splitext(path_parts[-1])[1])),
                              ('Accept-Ranges', 'bytes'),
                              ('Cache-Control', 'no-cache'),
                              ('Expires', '-1'),
                              ('DASH-Live-Simulator', SERVER_AGENT),
                              ('Access-Control-Allow-Headers', 'origin,range,accept-encoding,referer'),
                              ('Access-Control-Allow-Methods', 'GET,HEAD,OPTIONS'),
                              ('Access-Control-Allow-Origin', '*'),
                              ('Access-Control-Expose-Headers', 'Server,range,Content-Length,Content-Range,Date')])
    for chunk in dash_proxy.handle_request(environment['HTTP_HOST'],
                                           path_parts[1:],
                                           None,
                                           'vod_configs',
                                           'vod',
                                           time(),
                                           None,
                                           environment.get('HTTPS', 0)):
        yield chunk
