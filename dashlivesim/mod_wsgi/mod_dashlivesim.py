from sys import stderr
from dashlivesim import SERVER_AGENT
from os.path import splitext
from time import time
from dashlivesim.dashlib import dash_proxy
from collections import defaultdict


mime_map = defaultdict(lambda: 'text/plain', {'.mpd': 'application/dash+xml',
                                              '.m4s': 'video/iso.segment',
                                              '.mp4': 'video/mp4'})


headers = [('Accept-Ranges', 'bytes'),
           ('Pragma', 'no-cache'),
           ('Cache-Control', 'no-cache'),
           ('Expires', '-1'),
           ('DASH-Live-Simulator', SERVER_AGENT),
           ('Access-Control-Allow-Headers', 'origin,range,accept-encoding,referer'),
           ('Access-Control-Allow-Methods', 'GET,HEAD,OPTIONS'),
           ('Access-Control-Allow-Origin', '*'),
           ('Access-Control-Expose-Headers', 'Server,range,Content-Length,Content-Range,Date')]


def application(environment, start_response):
    path_parts = environment['REQUEST_URI'].split('/')
    start_response('200 OK', headers + [('Content-Type', mime_map[splitext(path_parts[-1])[1]])])
    for chunk in dash_proxy.handle_request(environment['HTTP_HOST'], path_parts[1:], None, environment['VOD_CONF_DIR'],
                                           environment['CONTENT_ROOT'], time(), None, environment.get('HTTPS', 0)):
        yield chunk


def main():
    """Run stand-alone wsgi server for testing."""
    from wsgiref.simple_server import make_server
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-d", "--config_dir", dest="vod_conf_dir", type=str,
                        help="configuration root directory", required=True)
    parser.add_argument("-c", "--content_dir", dest="content_dir", type=str,
                        help="content root directory", required=True)
    parser.add_argument("--host", dest="host", type=str, help="IPv4 host", default="0.0.0.0")
    parser.add_argument("--port", dest="port", type=int, help="IPv4 port", default=8059)
    args = parser.parse_args()

    def application_wrapper(env, resp):
        """Wrapper around application for local web server."""
        env['REQUEST_URI'] = env['PATH_INFO'] # Set REQUEST_URI from PATH_INFO
        env['VOD_CONF_DIR'] = args.vod_conf_dir
        env['CONTENT_ROOT'] = args.content_dir
        return application(env, resp)

    httpd = make_server(args.host, args.port, application_wrapper)
    httpd.serve_forever()
    print 'Waiting for requests at "%s:%d"' % (args.host, args.port)


if __name__ == '__main__':
    main()