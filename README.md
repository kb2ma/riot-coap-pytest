These tests exercise RIOT's CoAP implementations, [gcoap and nanocoap](https://github.com/RIOT-OS/RIOT/wiki/CoAP-Home). The tests are automated with the use of [pytest](https://pytest.org/).

With all of these tests, your confidence in the results will increase by watching the CoAP messages in Wireshark.

These tests all were developed using native on a recent Ubuntu Linux. Tests that use the gcoap example may be run on real hardware. See the _Setup_ section below for information on the required environment variables.

Materials
=========

In addition to pytest, you'll need a recent copy of these projects:

* [libcoap](https://github.com/obgm/libcoap)
* [aiocoap](https://github.com/chrysn/aiocoap)
* [soscoap](https://github.com/kb2ma/soscoap)

The _Setup_ section below assumes these projects are installed in source code form, not with pip or setup.py.

RIOT Examples
-------------
These tests use the following RIOT examples, which must be precompiled:

* gcoap
* nanocoap_server
* cord_ep
* cord_epsim

Setup
=====

Some of these tests use a tap interface to communicate between a native RIOT instance and the Linux desktop. They require an fd00:bbbb::/64 ULA-based network defined on the desktop as:
```
    $ sudo ip address add fd00:bbbb::1/64 dev tap0 scope global
```

Some tests do not allow specification of the address, so the test uses the TAP_LLADDR_SUT environment variable for the link local address. You can specify a link local address for tap with:
```
    sudo ip link set dev tap0 address 0:0:bb:bb:0:1
    sudo ip address add fe80::200:bbff:febb:1/64 dev tap0 scope link
```
Notice the tap interface address uses host '1', while the SUT address for the RIOT board must use host '2'.

Some tests require environment variables. See `setup_env.sh`. You MUST adapt it to the paths on your machine, but then you can source it with:
```
    $ . setup_env.sh
```
As mentioned in the _Materials_ section, presently the script is based on installation of aiocoap and soscoap in source form.

Running the tests
=================
You can run all tests in this directory with a single invocation of the standard `pytest` command. See the pytest [usage documentation](https://docs.pytest.org/en/latest/usage.html) for variations.
