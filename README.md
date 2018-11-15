These tests exercise RIOT's CoAP implementations, [gcoap and nanocoap](https://github.com/RIOT-OS/RIOT/wiki/CoAP-Home). The tests are automated with the use of [pytest](https://pytest.org/).

With all of these tests, your confidence in the results will increase by watching the CoAP messages in Wireshark.

These tests all were developed using native on a recent Ubuntu Linux. However, they all may be run just as well on hardware.

Materials
---------

In addition to pytest, you'll need a recent copy of these projects:

* [libcoap](https://github.com/obgm/libcoap)
* [aiocoap](https://github.com/chrysn/aiocoap)
* [soscoap](https://github.com/kb2ma/soscoap)

The _Setup_ section below assumes these projects are installed in source code form, not with pip or setup.py.

Setup
-----

Some of these tests use a tap interface to communicate between a native RIOT instance and the Linux desktop. They require an fd00:bbbb::/64 ULA-based network defined on the desktop as:
```
    $ sudo ip address add fd00:bbbb::1/64 dev tap0 scope global
```

Some tests require environment variables. See `setup_env.sh`. You MUST adapt it to the paths on your machine, but then you can source it with:
```
    $ . setup_env.sh
```
As mentioned in the _Materials_ section, presently the script is based on installation of aiocoap and soscoap in source form.

Running the tests
-----------------
You can run all tests in this directory with a single invocation of the standard `pytest` command. See the [usage documentation](https://docs.pytest.org/en/latest/usage.html) for variations.

### Details
gcoap attempts a maximum of four retries; five messages altogether including the initial request. The retries are timed with CoAP's exponential backoff mechanism.