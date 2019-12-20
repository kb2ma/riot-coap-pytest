# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests gcoap handling Observe registration, generating a notification, and
Observe cancellation.
"""

import pytest
import logging
import os
import time

from conftest import ExpectHost
from conftest import proto_params

pwd = os.getcwd()
#logging.basicConfig(level=logging.INFO, filename='run.log')

#
# fixtures and utility functions
#

@pytest.fixture
def aiocoap_client():
    """Registers an observe client and waits for a notification."""

    # server handles same quantity of messages as client sends
    dtls_arg = '-c dtls-credentials.json' if proto_params['is_dtls'] else ''
    cmd = './observe_client.py -r [fd00:bbbb::2] {0}'.format(dtls_arg)

    #host = ExpectHost(pwd, cmd, putenv={'PYTHONPATH' : '/home/kbee/dev/aiocoap/repo'})
    host = ExpectHost(pwd, cmd)
    term = host.connect()
    # allow a couple of seconds for initialization
    time.sleep(2)
    yield host

    # teardown
    host.disconnect()

#
# tests
#

@pytest.mark.parametrize('libcoap_port', ['5685'])
def test_observe(gcoap_example, aiocoap_client, libcoap_server):
    """Verify registration, notification, and cancellation."""
    # Registration OK; expecting 2 options -- Observer and Content-Format
    aiocoap_client.term.expect(r'First response:.*2\.05.*2 option')

    # send query to update stats and trigger notification
    dest_port = '5686' if proto_params['is_dtls'] else '5685'
    gcoap_example.send_recv('coap get -c fd00:bbbb::1 {0} /time'.format(dest_port),
                            r'Success')

    # Notification OK; expecting 2 options -- Observer and Content-Format
    aiocoap_client.term.expect(r'Next result:.*2\.05.*2 option')

    # Observe cancellation OK; expecting only 1 option -- Content-Format
    aiocoap_client.term.expect(r'Final result:.*2\.05.*1 option')
