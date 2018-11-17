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
    usage: repeat_send_client.py [-h] -r HOST

    optional arguments:
      -h, --help     show this help message and exit
      -r HOST        remote host for URI
      -q QTY         quantity of messages to handle

Example:

$ PYTHONPATH="/home/kbee/src/aiocoap" ./repeat_send_client.py -r [fd00:bbbb::2] -q 10
"""

import asyncio
import logging
import os
from argparse import ArgumentParser
from aiocoap import *

logfile ='repeat_send_client.log'
os.remove(logfile)
logging.basicConfig(level=logging.INFO, filename=logfile)

async def main(host, qty):
    context = await Context.create_client_context()

    for i in range(qty):
        await asyncio.sleep(2)
        request = Message(code=GET, uri='coap://{0}/cli/stats'.format(host))
        response = await context.request(request).response

        logging.info('Result: %s\n%r'%(response.code, response.payload))

if __name__ == "__main__":
    logging.info('parsing args')
    # read command line
    parser = ArgumentParser()
    parser.add_argument('-r', dest='host', required=True,
                        help='remote host for URI')
    parser.add_argument('-q', dest='qty', type=int, required=True,
                        help='quantity of messages to handle')

    args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(main(args.host, args.qty))
