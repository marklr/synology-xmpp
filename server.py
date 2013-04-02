#!/usr/bin/env python2.7
import logging
import xmpp
import sys
import traceback
from urlparse import parse_qsl

logger = logging.getLogger('synology-xmpp')

try:
    import config
except ImportError:
    raise RuntimeError("no config")


class BadRequest(Exception):
    pass


def send_xmpp_message(params, environ):
    try:
        user, dom = params['user'].strip().split('@')
        password = params['password'].strip()
        message = params['text'].strip()
    except (ValueError, KeyError) as e:
        raise BadRequest("Missing/invalid parameter: %s" % e)

    dests = config.DESTINATIONS
    if "to" in params and "@" in params.get('to', ''):
        dests += (params['to'].strip(), )
    for dst in dests:
        logger.info('Request: user=%s, to=%s: %s'.format(user, dst, message))
        try:
            client = xmpp.Client(dom)
            client.connect(server=config.XMPP_SERVER)
            client.auth(user=user, password=password, sasl=0)
            client.send(xmpp.Message(dst, message))
        except Exception as e:
            logger.warn(traceback.format_exc())
    return 'ok'


def app(environ, start_response):
    if environ.get('PATH_INFO', '').lstrip('/').rstrip('/') != '':
        start_response('200 OK', [('Content-type', 'text/plain')])
        return ['error 404']

    try:
        args = dict(parse_qsl(environ['QUERY_STRING']))
        response = send_xmpp_message(args, environ)
    except BadRequest, e:
        logger.error('Error: %s' % e)
        start_response('400 Bad Request', [('Content-type', 'text/plain')])
        return ['%s' % e]
    except Exception, e:
        logger.error('Error: %s' % e)
        raise
    else:
        logger.info('Success')
        start_response('200 Ok', [('Content-type', 'text/plain')])
        return [response]


def serve():
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', config.PORT, app)
    httpd.serve_forever()


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    if len(sys.argv) == 2 and sys.argv[1] == '-d':
        handler = logging.FileHandler(config.LOGFILE)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        import daemon  # doesn't work on Windows, btw.
        with daemon.DaemonContext(files_preserve=[handler.stream]):
            serve()
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        serve()
