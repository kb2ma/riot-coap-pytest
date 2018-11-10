#!/usr/bin/env python3

# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.
"""
Server that provides a time resource and allows for a delay before starting
the server.

/time -- time resource; GET only

Usage:
    usage: task05.py [-h] -d delay

    optional arguments:
      -h, --help  show this help message and exit
      -d DELAY    delay in seconds

Example:

$ PYTHONPATH="/home/kbee/src/aiocoap" ./con_retry_server.py -d 10
"""

import asyncio
import datetime
import logging
import time
from argparse import ArgumentParser

import aiocoap.resource as resource
from aiocoap import *

logging.basicConfig(level=logging.INFO)

class TimeResource(resource.Resource):
    """Handle GET for clock time."""
    async def render_get(self, request):
        payload = datetime.datetime.now().\
                strftime("%Y-%m-%d %H:%M").encode('ascii')
        msg = Message(payload=payload)
        msg.opt.content_format = 0
        return msg

def main(delay):
    # setup server resources
    root = resource.Site()
    root.add_resource(('time',), TimeResource())

    asyncio.Task(Context.create_server_context(root))

    time.sleep(delay)
    logging.info("con_retry_server listening")
    
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    # read command line
    parser = ArgumentParser()
    parser.add_argument('-d', dest='delay', type=int, default=0,
                        help='startup delay in seconds')

    args = parser.parse_args()

    main(args.delay)
