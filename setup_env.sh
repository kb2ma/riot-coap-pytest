# Environment variables for tests. Source this file before running them.
#
# Tests use environment variables rather than an INI file because it matches
# how the tests also would be run from within RIOT.

export RIOTBASE="/home/kbee/dev/riot/repo" 
export LIBCOAP_BASE="/home/kbee/dev/libcoap/repo"
export AIOCOAP_BASE="/home/kbee/dev/aiocoap/repo"
export SOSCOAP_BASE="/home/kbee/dev/soscoap/repo"
export BOARD="native"
# Link local address defined for the the RIOT board endpoint for the tap
# interface. Must include tap interface itself.
export TAP_LLADDR_SUT="fe80::200:bbff:febb:2%tap0"
# Link local address defined for the external test endpoint for the tap
# interface. Must *not* include the tap interface itself.
export TAP_LLADDR_EXT="fe80::200:bbff:febb:1"
export PYTHONPATH="${SOSCOAP_BASE}:${AIOCOAP_BASE}"
