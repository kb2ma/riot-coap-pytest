#!/usr/bin/env python3

# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.
"""
Test gcoap Observe implementation

Acts as client and observer for gcoap Observe server for /cli/stats resource.
Also acts as server for /time resource. gcoap requests time from aiocoap, which
updates gcoap's /cli/stats resource. This update triggers gcoap to send a
notification to aiocoap.

Expected result: aiocoap prints response code 2.05 and payload for initial
response to Observe request, and for following notification.

Usage:
    usage: observe_client.py -r HOST [-c FILE]
    usage: observe_client.py -h

    optional arguments:
      -h, --help  show this help message and exit
      -r HOST     remote host for URI
      -c FILE     DTLS credentials file, name format: *.json

2019-12-19 Added support here for DTLS use, but waiting on aiocoap DTLS server
support. See https://github.com/chrysn/aiocoap/issues/98.

Example:

$ PYTHONPATH="/home/kbee/src/aiocoap" ./observe_client.py -r [fd00:bbbb::2]

First response: <aiocoap.Message at 0x7f84dfa11c18: Type.ACK 2.05 Content
(MID 21466, token 6f1d) remote <UDP6EndpointAddress [fd00:bbbb::2]:5683 with
local address>, 2 option(s), 1 byte(s) payload>
b'0'

[gcoap requests /time]

Next result: <aiocoap.Message at 0x7f84dfa15240: Type.NON 2.05 Content
(MID 17807, token 6f1d) remote <UDP6EndpointAddress [fd00:bbbb::2]:5683 with
local address>, 2 option(s), 1 byte(s) payload>
b'1'

Loop ended, wait 10 sec
"""

import asyncio
import datetime
import json
import logging
from argparse import ArgumentParser
from conftest import proto_params
from pathlib import Path

import aiocoap.resource as resource
from aiocoap import *

class TimeResource(resource.Resource):
    """Handle GET for clock time."""

    async def render_get(self, request):
        payload = datetime.datetime.now().\
                strftime("%Y-%m-%d %H:%M").encode('ascii')
        msg = Message(payload=payload)
        msg.opt.content_format = 0
        return msg


async def main(host, credentialsFile):
    # setup server resources
    # As of 2019-12, not using server resources because DTLS server mode not
    # supported.
    root = resource.Site()
    root.add_resource(('time',), TimeResource())

    context = await Context.create_server_context(root)
    if proto_params['is_dtls']:
        context.client_credentials.load_from_dict(json.load(credentialsFile.open('rb')))

    uri = '{0}://{1}/cli/stats'.format(proto_params['uri_proto'], host)
    msg = Message(code=GET, uri=uri, observe=0)
    req = context.request(msg)

    resp = await req.response
    print('First response: %s\n%r'%(resp, resp.payload))

    async for resp in req.observation:
        # We expect some other process to send another request, which generates
        # an observe notification.
        print('Next result: %s\n%r'%(resp, resp.payload))

        req.observation.cancel()
        break

    # Send msg to cancel observation
    uri = '{0}://{1}/cli/stats'.format(proto_params['uri_proto'], host)
    msg = Message(code=GET, uri=uri, observe=1)
    req = context.request(msg)
    resp = await req.response
    print('Final result: %s\n%r'%(resp, resp.payload))

if __name__ == "__main__":
    # read command line
    parser = ArgumentParser()
    parser.add_argument('-r', dest='host', required=True,
                        help='remote host for URI')
    parser.add_argument('-c', dest='credentialsFile', type=Path,
                        help='DTLS credentials file, name format: *.json')

    args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(main(args.host,
                                                     args.credentialsFile))
