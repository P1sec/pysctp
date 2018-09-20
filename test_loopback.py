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

import sys
import time
import socket
import _sctp
import sctp


addr_client = ("127.0.0.1", 10002)
addr_server = ("127.0.0.1", 10001)

if _sctp.getconstant("IPPROTO_SCTP") != 132:
	raise(Exception("getconstant failed"))

def init_server():
    srv = sctp.sctpsocket_tcp(socket.AF_INET)
    srv.bind(addr_server)
    srv.listen(5)
    return srv

def test_cli():
    srv = init_server()
    #
    cli = sctp.sctpsocket_tcp(socket.AF_INET)
    # config SCTP number of streams
    cli.initparams.max_instreams = 3
    cli.initparams.num_ostreams = 3
    # disable SCTP events
    cli.events.clear()
    cli.events.data_io = 1
    #
    cli.bind(addr_client)
    cli.connect(addr_server)
    #
    buf = b"ABCDEF: TEST SUCCEEDED (test_local_cnx.py (C) 2009 Philippe Langlois)\n\l"
    cli.sctp_send(buf)
    print("client sctp_send: %s" % buf)
    print("")
    #
    time.sleep(0.01)
    #
    srv_to_cli, _addr_client = srv.accept()
    fromaddr, flags, msgret, notif = srv_to_cli.sctp_recv(2048)
    print("server sctp_recv, flag %d" % flags)
    print("server sctp_recv, buf: %s" % msgret)
    print("")
	#
    cli.close()
    time.sleep(0.01)
    srv.close()
    #
    return 0

if __name__ == '__main__':
    sys.exit(test_cli())

