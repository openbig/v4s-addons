#! /bin/sh
# -*- encoding: utf-8 -*-
#
# Written by Alexis de Lattre <alexis.delattre@akretion.com>

# Example of wrapper for get_cid_name.py which makes sure that the
# script doesn't take too much time to execute

# Limiting the execution time of get_cid_name.py is important because
# the script is designed to be executed at the beginning of each
# incoming phone call... and if the script get stucks, the phone call
# will also get stucks and you will miss the call !

# For Debian Lenny and Ubuntu Lucid, you need to install the package "timeout"
# For Ubuntu >= Maverick and Debian >= Squeeze, the "timeout" command is shipped
# in the "coreutils" package

# The first argument of the "timeout" command is the maximum execution time
# In this example, we chose 2 seconds. Note that geolocalisation takes about
# 1 second on an small machine ; so if you enable the --geoloc option,
# don't put a 1 sec timeout !

# To test this script manually (i.e. outside of Asterisk), run :
# echo "agi_callerid:0141981242"|get_cid_name_timeout.sh
# where 0141981242 is a phone number that could be presented by the calling party

PATH=/usr/local/sbin:/usr/local/bin:/var/lib/asterisk/agi-bin:/sbin:/bin:/usr/sbin:/usr/bin

#get relative path to the script's directory
SELF_PATH=`dirname "$0"`

#PYTHON_BIN="python"
PYTHON_BIN="$SELF_PATH/python-static-linux-x86" #python 2.7 static binary
GET_CID_NAME_PY="$SELF_PATH/get_cid_name.py"

# uncomment the correct timeout implementation
#TIMEOUT_CMD="timeout 2s" #GNU timeout
TIMEOUT_CMD="timeout -t 2" #busybox timeout

# OpenERP-Server access credentials
#SERVER="192.168.120.120"
SERVER="via4spine.remote.openbig.org"
#PORT="8069"
PORT="10346"
DATABASE="via4spine_test"
USER_ID="16"
PASSWORD="uAMOTMWn5XlHB9Py4AfH"
#SSL_OPT="--ssl"

# Settings with geolocalization enabled (requires python phonenumbers)
#eval $TIMEOUT_CMD $PYTHON_BIN $GET_CID_NAME_PY --server $SERVER $SSL_OPT --database $DATABASE  --user-id $USER_ID --password "$PASSWORD" --geoloc --geoloc-country "DE" --geoloc-lang "de"

# Settings for testing with OpenBIG-Remote external Access (using test db)
eval $TIMEOUT_CMD $PYTHON_BIN $GET_CID_NAME_PY --server $SERVER $SSL_OPT --port=$PORT --database $DATABASE  --user-id $USER_ID --password "$PASSWORD"
