#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 
# Copyright (C) 2009 Philippe Langlois - all rights reserved
#
# Test with sctp_test from lksctp:
# sctp_test -H 127.0.0.1 -P 10000 -l
#
# Test with sctpscan from P1 Security / Philippe Langlois:
# sctpscan -d
#
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; If not, see <http://www.gnu.org/licenses/>.

"""
Test with sctp_test from lksctp:
sctp_test -H 127.0.0.1 -P 10000 -l

Then run:
python ./test_local_cnx.py
or
python3 ./test_local_cnx.py
"""

import _sctp
import sctp
from sctp import *
import time

client = "127.0.0.1"
server = "127.0.0.1" 
tcpport = 10000

if _sctp.getconstant("IPPROTO_SCTP") != 132:
	raise(Exception("getconstant failed"))
tcp = sctpsocket_tcp(socket.AF_INET)

saddr = (server, tcpport)
 
print("TCP %r ----------------------------------------------" % (saddr, ))

tcp.initparams.max_instreams = 3
tcp.initparams.num_ostreams = 3

tcp.events.clear()
tcp.events.data_io = 1

tcp.connect(saddr)

tcp.sctp_send(b"ABCDEF: TEST SUCCEEDED (test_local_cnx.py (C) 2009 Philippe Langlois)\n\l")
while 1:
    fromaddr, flags, msgret, notif = tcp.sctp_recv(1000)
    print(" Msg arrived, flag %d" % flags)

    if flags & FLAG_NOTIFICATION:
        raise(Exception("We did not subscribe to receive notifications!"))
    #else:
    print("%s" % msgret)

tcp.close()
