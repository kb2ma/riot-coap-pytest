#!/usr/bin/env python

from argparse import ArgumentParser
import datetime
import logging
from   soscoap.server   import CoapServer, IgnoreRequestException

logging.basicConfig(level=logging.INFO)

class ConIgnoreServer(object):
    """
    Provides a server that ignores a configurable number of confirmable
    message attempts.
    """
    def __init__(self, ignores):
        """Pass in count of confirmable messages to ignore."""
        self._server = CoapServer(port=5683)
        self._server.registerForResourceGet(self._getResource)
        self._ignores = ignores

    def _getResource(self, resource):
        '''Sets the value for the provided resource, for a GET request.'''
        logging.info("resource path: {0}".format(resource.path))
        if resource.path == '/time':
            if self._ignores > 0:
                self._ignores = self._ignores - 1
                raise IgnoreRequestException
                return
            else:
                resource.type  = 'string'
                now = datetime.datetime.now()
                resource.value = now.strftime("%Y-%m-%d %H:%M").encode('ascii')
        else:
            raise NotImplementedError('Unknown path')
            return

    def start(self):
        self._server.start()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-i', dest='ignores', type=int, default=3,
                        help='count of requests to ignore')

    args = parser.parse_args()

    server = ConIgnoreServer(args.ignores)
    server.start()


