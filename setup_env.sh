# Environment variables for tests. Source this file before running them.
#
# Using environment variables rather than an INI file because it matches
# how the tests would be run from within RIOT.

export RIOTBASE="/home/kbee/dev/riot/repo" 
export LIBCOAP_BASE="/home/kbee/dev/libcoap/repo"
export AIOCOAP_BASE="/home/kbee/dev/aiocoap/repo"
export PYTHONPATH="${AIOCOAP_BASE}"
