#!/usr/bin/env python3

# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.
"""
Repeat sending simple GET to RIOT instance. Logs each message received so they
may be validated. Waits two seconds between sends.

Expected result:

Usage:
    usage: repeat_send_client.py [-c FILE] -r HOST -p PATH -q QTY
    usage: repeat_send_client.py -h

    optional arguments:
      -h, --help     show this help message and exit
      -p PATH        path for URI
      -r HOST        remote host for URI
      -q QTY         quantity of messages to handle
      -c FILE        DTLS credentials file, name format: *.json

Example:

$ PYTHONPATH="/home/kbee/src/aiocoap" ./repeat_send_client.py -p /cli/stats -r [fd00:bbbb::2] -q 10
"""

import asyncio
import contextlib
import json
import logging
import os
from argparse import ArgumentParser
from aiocoap import *
from conftest import proto_params
from pathlib import Path

logfile = 'repeat_send_client.log'
with contextlib.suppress(FileNotFoundError):
    os.remove(logfile)

logging.basicConfig(level=logging.INFO, filename=logfile)

async def main(host, path, qty, credentialsFile=None):
    context = await Context.create_client_context()
    if proto_params['is_dtls']:
        context.client_credentials.load_from_dict(json.load(credentialsFile.open('rb')))

    for i in range(qty):
        await asyncio.sleep(2)
        request = Message(code=GET, uri='{0}://{1}{2}'.format(proto_params['uri_proto'],
                                                              host, path))
        response = await context.request(request).response

        logging.info('Result: %s\n%r'%(response.code, response.payload))

if __name__ == "__main__":
    logging.info('parsing args')
    # read command line
    parser = ArgumentParser()
    parser.add_argument('-r', dest='host', required=True,
                        help='remote host for URI')
    parser.add_argument('-p', dest='path', required=True,
                        help='URI path for resource')
    parser.add_argument('-q', dest='qty', type=int, required=True,
                        help='quantity of messages to handle')
    parser.add_argument('-c', dest='credentialsFile', type=Path,
                        help='DTLS credentials file, name format: *.json')

    args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(main(args.host, args.path, args.qty,
                                                     args.credentialsFile))
