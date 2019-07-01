These tests exercise RIOT's CoAP implementations, [gcoap and nanocoap](https://github.com/RIOT-OS/RIOT/wiki/CoAP-Home). The tests are automated with the use of [pytest](https://pytest.org/).

With all of these tests, your confidence in the results will increase by watching the CoAP messages in Wireshark.

These tests all were developed using native on a recent Ubuntu Linux. Tests that use the gcoap example may be run on real hardware. See the _Setup_ section below for information on the required environment variables.

Materials
=========

In addition to pytest, you'll need a recent copy of these projects:

|  Project  | Notes |
| --------- | ----- |
| [aiocoap](https://github.com/chrysn/aiocoap) | must install linkheader Python package; see the *Slimmer installations* portion of aiocoap docs |
| [libcoap](https://github.com/obgm/libcoap) | |
| [soscoap](https://github.com/kb2ma/soscoap) | |
[riot-apps](https://github.com/kb2ma/riot-apps) | forked from RIOT-OS/applications; use kb2ma-master branch |

The _Setup_ section below assumes these projects are installed in source code form, not with pip or setup.py.

RIOT Tools
----------
These tests use the following RIOT based tools, which must be precompiled:

|        Tool        |  Location  |    Status     | Notes |
| ------------------ | ---------- | ------------- | ----- |
| gcoap              | examples   |               |       |
| nanocoap_server    | examples   |               |       |
| cord_ep            | examples   | 2019-07-01 OK |       |
| cord_epsim         | examples   | 2019-07-01 OK | when compile for native2os endpoints, must specify RD_ADDR as TAP_LLADDR_REMOTE from `setup_env.sh`; otherwise aiocoap fails with the default multicast address on local |
| nanocoap_cli       | tests      |               |       |
| gcoap-block-server | riot-apps  |               |       |
| gcoap-block-client | riot-apps  |               |       |
| nano-block-client  | riot-apps  |               |       |


Setup
=====
The network/board interfaces used for tests have evolved over time. The table below show the currently supported setups.


|       Test       |     Endpoints      |      SUT           |  Tools  | Notes |
| ---------------- | ------------------ | ------------------ | ------- | ----- |
| block1_server    | native2os          | nanocoap_server, gcoap-block-server | aiocoap | |
| block2_server    | native2os          | nanocoap_server, gcoap-block-server | aiocoap | |
| block1_client    | native2native      | nano-block-client, gcoap-block-client | gcoap-block-server | |
| block2_client    | native2native      | nano-block-client, gcoap | gcoap-block-server | |
| con_retry        | native2os          | gcoap              | aiocoap | |
| cord_ep          | native2os, slip2os | cord_ep (gcoap)    | aiocoap | |
| cord_epsim       | native2os, slip2os | cord_epsim (gcoap) | aiocoap, libcoap | |
| observe          | native2os, slip2os | gcoap              | aiocoap | |
| request_response | native2os          | nanocoap_cli, gcoap | libcoap, aiocoap | |
| request_response | slip2os            | gcoap              | libcoap, aiocoap | Must run gcoap tests one by one to avoid running the nanocoap test. |

Each test named above is implemented in the file **[name]_test.py**.

native2os
---------
Some of these tests use a tap interface to communicate between a native RIOT instance and the Linux desktop. They require an fd00:bbbb::/64 ULA-based network defined on the desktop as:
```
    $ sudo ip address add fd00:bbbb::1/64 dev tap0 scope global
```

Some tests do not allow specification of the address, so the test uses the TAP_LLADDR_SUT environment variable for the link local address for the RIOT endpoint, and TAP_LLADR_REMOTE for the address of the OS endopint. You can specify a link local address for tap with:
```
    sudo ip link set dev tap0 address 0:0:bb:bb:0:1
    sudo ip address add fe80::200:bbff:febb:1/64 dev tap0 scope link
```
Notice the REMOTE tap interface address uses host '1', while the SUT address for the RIOT board must use host '2'.

Some tests require environment variables. See `setup_env.sh`. You MUST adapt it to the paths on your machine, but then you can source it with:
```
    $ . setup_env.sh
```
As mentioned in the _Materials_ section, presently the script is based on installation of aiocoap and libcoap in source form.

native2native
-------------
Some tests use a tap bridge to communicate between two RIOT instances. In this case the OS generates the link local network addresses, so the CoAP server in the test must be able to set up a ULA so the client knows the address for the server. The tap bridge is setup with:

```
    $ cd $RIOTBASE/dist/tools/tapsetup/
    $ ./tapsetup -c 2

    # to delete the tap
    $ ./tapsetup -d
```

slip2os
-------
Some tests allow use of a physical board for the RIOT instance. They require an fd00:bbbb::/64 ULA-based network defined on the desktop as:

```
    $ cd $RIOTBASE/dist/tools/tunslip/
    $ sudo ./tunslip6 -s ttyUSB0 -t tun0 fd00:bbbb::1/64
```

rpl2os
------
This setup allows use of a physical board via RPL to a Linux host. This setup requires two boards:

  * RPL root node attached to the Linux host, running the gnrc_border_router example
  * RPL leaf node running gcoap/nanocoap

**RPL root node**

For this node, we specify the address of the wireless interface on the fd00:aaaa::/64 network. Then we initialize the node as RPL root.

**NOTE** The _make term_ step below includes initialization of the address and routing on the Linux host, and then starts the terminal.

This setup is based on the gnrc_border_router example. First, ensure that the gnrc_rpl module is included in the Makefile.

As mentioned below, ethos sets up border routing. By default, it defines fd00:dead:beef:: as the network on the wired/cloud side. You must manually update `dist/tools/ethos/start_network.sh` to use a different address for the network.

Reminder for samr21-xpro: a udev rule is required for an unprivileged user to flash this board. See `boards/samr21-xpro/doc.txt`.

```
    # To determine serial port, if more than one board attached
    $ ../../dist/tools/usb-serial/list-ttys.sh

    $ BOARD="samr21-xpro" make clean all flash SERIAL="<serial-number>"

    # This step automatically starts ethos to set up border routing. The terminal
    # is available for command input/output.
    $ BOARD="samr21-xpro" IPV6_PREFIX="fd00:aaaa::/64" PORT="/dev/ttyACM0" make term

    # Manually setting address is a convenience so don't have to search for it.
    > ifconfig 6 add unicast fd00:aaaa::1/64
    > rpl init 6
    > rpl root 1 fd00:aaaa::1
```


**RPL leaf node**

First, ensure that the gnrc_rpl module is included in the Makefile.

After setting up the RPL root node, just initialize rpl for the leaf node. RPL decides the address on the fd00:aaaa::/64 network to use.

```
    # May encounter an issue with pyterm unable to find serial module.
    # If so, change #! command in pyterm module to use python3
    $ BOARD="samr21-xpro" make clean all flash SERIAL="???"
    $ BOARD="samr21-xpro" PORT="/dev/ttyACM1" make term

    # Interface number may differ
    > rpl init 6
    # Use the fd00:aaaa::/64 address from this command
    > ifconfig
```


Running the tests
=================
See the pytest [usage documentation](https://docs.pytest.org/en/latest/usage.html) for variations.
