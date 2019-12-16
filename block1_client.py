#!/usr/bin/env python3

# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.
"""
Test nanocoap Block1 server response to SHA256 hash request payload

Expected result: aiocoap prints response code 2.04 and SHA256 digest

Usage:
    usage: block1_client.py -r HOST [-b BLOCK_SIZE] [-c FILE]
    usage: block1_client.py -h

    optional arguments:
      -h, --help     show this help message and exit
      -r HOST        remote host for URI
      -b BLOCK_SIZE  one of 16, 32, 64, ..., 1024
      -c FILE        DTLS credentials file, name format: *.json

Example:

$ PYTHONPATH="/home/kbee/src/aiocoap" ./block1_client.py -r [fe80::200:bbff:febb:2%tap0]

Result: 2.04 Changed
b'C496DF5946783990BEC5EFDC2999530EEB9175B83094BAE66170FF2431FC896E'
"""

import logging
import asyncio
import json
import math
from argparse import ArgumentParser
from aiocoap import *
from conftest import proto_params
from pathlib import Path

logging.basicConfig(level=logging.INFO)

async def main(host, block_size, credentialsFile=None):
    # create async context and wait a couple of seconds
    context = await Context.create_client_context()
    if proto_params['is_dtls']:
        context.client_credentials.load_from_dict(json.load(credentialsFile.open('rb')))
    await asyncio.sleep(2)

    payload = b'If one advances confidently in the direction of his dreams...'

    request = Message(code=POST, payload=payload,
                      uri='{0}://{1}/sha256'.format(proto_params['uri_proto'], host))

    block_exp = round(math.log(block_size, 2)) - 4
    request.opt.block1 = optiontypes.BlockOption.BlockwiseTuple(0, 0, block_exp)

    response = await context.request(request).response

    print('Result: %s\n%r'%(response.code, response.payload))

if __name__ == "__main__":
    # read command line
    parser = ArgumentParser()
    parser.add_argument('-r', dest='host', required=True,
                        help='remote host for URI')
    parser.add_argument('-b', dest='block_size', type=int, default=32,
                        help='one of 16, 32, 64, ..., 1024')
    parser.add_argument('-c', dest='credentialsFile', type=Path,
                        help='DTLS credentials file, name format: *.json')

    args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(main(args.host, args.block_size,
                                                     args.credentialsFile))
