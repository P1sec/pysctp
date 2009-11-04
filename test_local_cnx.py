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
import _sctp
import sctp
from sctp import *
import time

client = "127.0.0.1"
server = "127.0.0.1" 
tcpport = 10000

if _sctp.getconstant("IPPROTO_SCTP") != 132:
	raise "getconstant failed"
tcp = sctpsocket_tcp(socket.AF_INET)

saddr = (server, tcpport)
 
print "TCP ", saddr, " ----------------------------------------------"

tcp.initparams.max_instreams = 3
tcp.initparams.num_ostreams = 3

tcp.events.clear()
tcp.events.data_io = 1

tcp.connect(saddr)

tcp.sctp_send("ABCDEF: TEST SUCCEEDED (test_local_cnx.py (C) 2009 Philippe Langlois)\n\l")
while 1:
    fromaddr, flags, msgret, notif = tcp.sctp_recv(1000)
    print "	Msg arrived, flag %d" % flags

    if flags & FLAG_NOTIFICATION:
        raise "We did not subscribe to receive notifications!"
    else:
	print "%s" % msgret

tcp.close()
