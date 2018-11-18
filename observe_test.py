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
import os
import time

from conftest import ExpectHost

pwd = os.getcwd()

#
# fixtures and utility functions
#

@pytest.fixture
def aiocoap_client():
    """Registers an observe client and waits for a notification."""
    # server handles same quantity of messages as client sends
    cmd = './observe_client.py -r [fd00:bbbb::2]'

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

def test_observe(gcoap_example, aiocoap_client):
    """Verify registration, notification, and cancellation."""
    # Registration OK; expecting 2 options -- Observer and Content-Format
    aiocoap_client.term.expect(r'First response:.*2\.05.*2 option')

    # send query to update stats and trigger notification
    gcoap_example.send_recv('coap get -c fd00:bbbb::1 5683 /time',
                            r'Success')

    # Notification OK; expecting 2 options -- Observer and Content-Format
    aiocoap_client.term.expect(r'Next result:.*2\.05.*2 option')

    # Observe cancellation OK; expecting only 1 option -- Content-Format
    aiocoap_client.term.expect(r'Final result:.*2\.05.*1 option')
