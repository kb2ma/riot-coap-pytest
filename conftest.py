# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Utilities for tests
"""

import pytest
import pexpect
import os
import signal
import logging

class ExpectHost():
    """
    A networking host wrapped in a pexpect spawn. There are two ways to run
    the host:

    1. connect() to start an interactive session, followed by send_recv() or
       directly sending commands from the returned pexpect 'term' object.
       Finally, use disconnect() to kill the session.

    2. run() to start and run the process to completion with no interaction.
    """

    def __init__(self, folder, term_cmd, timeout=10):
        self.folder = folder
        self.term = None
        self.term_cmd = term_cmd
        self.timeout = timeout

    def connect(self):
        """
        Starts OS host process.

        :return: pexpect spawn object; the 'term' attribute for ExpectHost
        """
        if self.folder:
            os.chdir(self.folder)
        
        self.term = pexpect.spawnu(self.term_cmd, codec_errors='replace',
                                  timeout=self.timeout)
        return self.term

    def run(self):
        """
        Runs OS host process to completion

        :return: String output from process
        """
        if self.folder:
            os.chdir(self.folder)
        return pexpect.run(self.term_cmd)

    def disconnect(self):
        """Kill OS host process"""
        try:
            os.killpg(os.getpgid(self.term.pid), signal.SIGKILL)
        except ProcessLookupError:
            logging.info("Process already stopped")

    def send_recv(self, out_text, in_text):
        """Sends the given text to the host, and expects the given text
           response."""
        self.term.sendline(out_text)
        self.term.expect(in_text, self.timeout)


@pytest.fixture
def gcoap_example():
    """
    Runs the RIOT gcoap CLI example as an ExpectHost.
    """
    base_folder = os.environ.get('RIOTBASE', None)

    host = ExpectHost(os.path.join(base_folder, 'examples/gcoap'), 'make term')
    term = host.connect()
    term.expect('gcoap .* app')

    # set ULA
    host.send_recv('ifconfig 6 add unicast fd00:bbbb::2/64',
                   'success:')
    yield host

    # teardown
    host.disconnect()


@pytest.fixture
def nanocoap_server():
    """
    Runs the RIOT nanocoap server example as an ExpectHost. It does not provide
    a CLI to customize network addresses. So, it is easiest to specify the link
    address when defining the tap interface on the test host.
    """
    base_folder = os.environ.get('RIOTBASE', None)

    host = ExpectHost(os.path.join(base_folder, 'examples/nanocoap_server'),
                                   'make term')
    term = host.connect()
    term.expect('Configured network interfaces')
    yield host

    # teardown
    host.disconnect()


def pytest_addoption(parser):
    """Updates configuration within startup hook"""
    # for request_response_test.py
    parser.addini('request_response_repeat', 'number of times to repeat the test',
                  default='1')
