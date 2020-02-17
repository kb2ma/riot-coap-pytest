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

    def __init__(self, folder, term_cmd, putenv={}, timeout=10):
        """
        :putenv: Additional entries for os.environ dictionary to pass to
                 spawned process
        """
        self.folder   = folder
        self.term     = None
        self.term_cmd = term_cmd
        self.timeout  = timeout
        self.putenv   = putenv

    def connect(self):
        """
        Starts OS host process.

        :return: pexpect spawn object; the 'term' attribute for ExpectHost
        """
        if self.folder:
            os.chdir(self.folder)

        self.term = pexpect.spawnu(self.term_cmd, timeout=self.timeout,
                                   env=self._build_env(), codec_errors='replace')
        return self.term

    def run(self):
        """
        Runs OS host process to completion

        :return: String output from process
        """
        if self.folder:
            os.chdir(self.folder)
        return pexpect.run(self.term_cmd, env=self._build_env())

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

    def _build_env(self):
        """Builds full os.environ dictionary if putenv instance variable has
           been defined."""
        env = None
        if self.putenv:
            env = os.environ.copy()
            env.update(self.putenv)
        return env

# Protocol level parameters -- DTLS vs. UDP
proto_params = {}
if (os.environ.get('TRANSPORT_PROTOCOL', 'UDP') == 'DTLS'):
    proto_params['is_dtls'] = True
    proto_params['uri_proto'] = 'coaps'
    proto_params['port'] = 5684
    proto_params['psk_key'] = 'secretPSK'
    proto_params['psk_id'] = 'Client_identity'
    proto_params['session_setup_msgs'] = 6
else:
    proto_params['is_dtls'] = False
    proto_params['uri_proto'] = 'coap'
    proto_params['port'] = 5683
    proto_params['session_setup_msgs'] = 0


@pytest.fixture
def gcoap_example():
    """
    Runs the RIOT gcoap CLI example as an ExpectHost. Uses BOARD environment
    variable to run on real hardware.
    """
    base_folder = os.environ.get('RIOTBASE', None)
    board       = os.environ.get('BOARD', 'native')

    if board == 'native':
        term_cmd = 'make term'
        term_resp = 'gcoap .* app'
    else:
        term_cmd = 'make term BOARD="{0}"'.format(board)
        term_resp = 'Welcome to pyterm!'
        
    host = ExpectHost(os.path.join(base_folder, 'examples/gcoap'), term_cmd)
    term = host.connect()
    term.expect(term_resp)

    # set ULA
    if board == 'native':
        pid = '5' if proto_params['is_dtls'] else '6'
        host.send_recv('ifconfig {0} add unicast fd00:bbbb::2/64'.format(pid),
                       'success:')
    else:
        host.send_recv('ifconfig 8 add unicast fd00:bbbb::2/64',
                        'success:')
        term.sendline('nib neigh add 8 fd00:bbbb::1')
        host.send_recv('nib neigh', 'fd00:bbbb::1')
    yield host

    # teardown
    host.disconnect()


@pytest.fixture
def nanocoap_server():
    """
    Runs the RIOT nanocoap server example as an ExpectHost. It does not provide
    a CLI to customize network addresses. So, it is easiest to specify the link
    address when defining the tap interface on the test host. Tests usually
    expect the environment variable TAP_LLADDR for this address.
    """
    base_folder = os.environ.get('RIOTBASE', None)

    host = ExpectHost(os.path.join(base_folder, 'examples/nanocoap_server'),
                                   'make term')
    term = host.connect()
    term.expect('Configured network interfaces')
    yield host

    # teardown
    host.disconnect()

@pytest.fixture
def nanocoap_cli():
    """
    Runs the RIOT nanocoap CLI test app as an ExpectHost. Cannot explicitly
    set network addressing due to limitations of the app.
    """
    base_folder = os.environ.get('RIOTBASE', None)

    host = ExpectHost(os.path.join(base_folder, 'tests/nanocoap_cli'), 'make term')
    term = host.connect()
    term.expect('nanocoap test app')

    yield host

    # teardown
    host.disconnect()

@pytest.fixture
def libcoap_client(request_path):
    """Runs a libcoap example client as an ExpectHost to retrieve a response."""
    folder = os.environ.get('LIBCOAP_BASE', None)
    cmd_folder = folder + '/examples/' if folder else ''
    if proto_params['is_dtls']:
        dtls_arg = '-k {0} -u {1}'.format(proto_params['psk_key'],
                                          proto_params['psk_id'])
    else:
        dtls_arg = ''

    cmd = '{0}coap-client {1} -N -m get -T 5a -U {2}://[fd00:bbbb::2]{3}'
    cmd_text = cmd.format(cmd_folder, dtls_arg, proto_params['uri_proto'], request_path)

    host = ExpectHost(folder, cmd_text)
    yield host

@pytest.fixture(scope='session')
def libcoap_port():
    """Provides default value for libcoap_server fixture port."""
    return '5683'

@pytest.fixture(scope='session')
def libcoap_ignore_count():
    """Provides default value for libcoap_server fixture port. This value is
       the count of requests the server will ignore. This ability is useful
       for testing confirmable retries."""
    return 0

@pytest.fixture
def libcoap_server(libcoap_port, libcoap_ignore_count):
    """Runs a libcoap example server process, and provides a pexpect spawn
       object to interact with it."""
    folder = os.environ.get('LIBCOAP_BASE', None)
    if proto_params['is_dtls']:
        dtls_arg = '-k {0}'.format(proto_params['psk_key'])
    else:
        dtls_arg = ''
        
    ignore_low = 1 + proto_params['session_setup_msgs']
    ignore_high = libcoap_ignore_count + proto_params['session_setup_msgs']
    ignore_range_arg = '-l {0}-{1}'.format(ignore_low, ignore_high) if libcoap_ignore_count else ''

    cmd = '{0}coap-server -p {1} {2} {3}'.format('examples/' if folder else '',
                                             libcoap_port, dtls_arg, ignore_range_arg)

    host = ExpectHost(folder, cmd)
    term = host.connect()
    yield host

    # teardown
    host.disconnect()

#
# hooks
#

def pytest_addoption(parser):
    """Updates configuration within startup hook"""
    # for request_response_test.py
    parser.addini('request_response_repeat', 'number of times to repeat the test',
                  default='1')
