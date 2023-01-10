#!/usr/bin/env python3

import sys
import argparse
import sctp
from socket     import *
from select     import select
from threading  import Event
from time       import sleep
from datetime   import datetime
from binascii   import hexlify


SRV_ADDR    = '127.0.0.1'
SRV_PORT    = 9999
SRV_MAXCLI  = 10

# maximum DATA chunk size
# if set to 0, relies on the current OS config
SCTP_MAXSEG = 0
# maximum buffer size available for SCTP read / write
# ensure it is below the OS limits in /proc/sys/net/core/{w,r}mem_max
SCTP_RMAX   = 16384
SCTP_WMAX   = 16384
# select call timeout
SCTP_SELTO  = 0.1


def sk_set_events(sk):
    """events subscribed for the echo server SCTP socket
    """
    # to receive PPID, stream and other ancilliary info with data payload 
    sk.events.data_io           = True
    # to receive events related to association parameters changes
    sk.events.association       = True
    # to receive events related to 
    sk.events.address           = True
    sk.events.send_failure      = True
    sk.events.peer_error        = True
    sk.events.shutdown          = True
    sk.events.partial_delivery  = True
    sk.events.adaptation_layer  = True
    # default behavior is autoflush, we don't need to flush() explicitely
    #sk.events.flush()


#------------------------------------------------------------------------------#
# custom ways to print information to user
#------------------------------------------------------------------------------#

def log(msg='', withdate=True):
    if withdate:
        msg = '[%s] %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], msg)
    print(msg)


def log_sockinfos(sk):
    msg = [    'SCTP socket parameters, fd %i:' % sk.fileno()]
    # SCTP assoc initparams
    msg.append('  sk.initparams.num_ostreams     : %i' % sk.initparams.num_ostreams)
    msg.append('  sk.initparams.max_instreams    : %i' % sk.initparams.max_instreams)
    msg.append('  sk.initparams.max_attempts     : %i' % sk.initparams.max_attempts)
    msg.append('  sk.initparams.max_init_timeo   : %i' % sk.initparams.max_init_timeo)
    # SCTP events supported by pysctp
    msg.append('  sk.events.data_io              : %s' % sk.events.data_io)
    msg.append('  sk.events.association          : %s' % sk.events.association)
    msg.append('  sk.events.address              : %s' % sk.events.address)
    msg.append('  sk.events.send_failure         : %s' % sk.events.send_failure)
    msg.append('  sk.events.peer_error           : %s' % sk.events.peer_error)
    msg.append('  sk.events.shutdown             : %s' % sk.events.shutdown)
    msg.append('  sk.events.partial_delivery     : %s' % sk.events.partial_delivery)
    msg.append('  sk.events.adaptation_layer     : %s' % sk.events.adaptation_layer)
    log('\n'.join(msg), withdate=False)


def log_sndrcvinfo(srinf, ret=False):
    msg = [    '  srinf.assoc_id         : %i' % srinf.assoc_id]
    msg.append('  srinf.stream           : %i' % srinf.stream)
    msg.append('  srinf.ssn              : %i' % srinf.ssn)
    msg.append('  srinf.flags            : %i' % srinf.flags)
    msg.append('  srinf.ppid             : %i' % ntohl(srinf.ppid))
    msg.append('  srinf.context          : %i' % srinf.context)
    msg.append('  srinf.timetolive       : %i' % srinf.timetolive)
    msg.append('  srinf.tsn              : %i' % srinf.tsn)
    msg.append('  srinf.cumtsn           : %i' % srinf.cumtsn)
    if ret:
        return '\n'.join(msg)
    else:
        log('\n'.join(msg), withdate=False)


def log_notifinfos(notif):
    msg = []
    #msg.append('  notif.type             : %s' % notif.type)
    #msg.append('  notif.flags            : %s' % notif.flags)
    if isinstance(notif, sctp.assoc_change):
        msg.append('  notif.assoc_id         : %s' % notif.assoc_id)
        msg.append('  notif.state            : %i - %s' % (notif.state, interpret_state(notif.state, sctp.assoc_change)))
        msg.append('  notif.error            : %i - %s' % (notif.error, interpret_error(notif.error, sctp.assoc_change)))
        msg.append('  notif.outbound_streams : %s' % notif.outbound_streams)
        msg.append('  notif.inbound_streams  : %s' % notif.inbound_streams)
    elif isinstance(notif, sctp.paddr_change):
        msg.append('  notif.assoc_id         : %s' % notif.assoc_id)
        msg.append('  notif.state            : %i - %s' % (notif.state, interpret_state(notif.state, sctp.paddr_change)))
        msg.append('  notif.error            : %i - %s' % (notif.error, interpret_error(notif.error, sctp.paddr_change)))
        msg.append('  notif.addr             : %r' % (notif.addr, ))
    elif isinstance(notif, sctp.remote_error):
        msg.append('  notif.assoc_id         : %s' % notif.assoc_id)
        msg.append('  notif.error            : %s' % notif.error)
        msg.append('  notif.data             : %s' % notif.data)
    elif isinstance(notif, sctp.send_failed):
        msg.append('  notif.assoc_id         : %s' % notif.assoc_id)
        msg.append('  notif.error            : %s' % notif.error)
        msg.append('  notif.data             : %s' % notif.data)
        msg.append('  notif.info             : srinf')
        msg.append(log_sndrcvinfo(notif.info, log=False))
    elif isinstance(notif, sctp.shutdown_event):
        msg.append('  notif.assoc_id         : %s' % notif.assoc_id)
    elif isinstance(notif, sctp.adaptation_event):
        msg.append('  notif.assoc_id         : %s' % notif.assoc_id)
        msg.append('  notif.adaptation_ind   : %s' % ntohl(notif.adaptation_ind))
    elif isinstance(notif, sctp.pdapi_event):
        msg.append('  notif.assoc_id         : %s' % notif.assoc_id)
        msg.append('  notif.indication       : %s' % notif.indication)
    else:
        msg.append('  notification unknown from pysctp')
    log('\n'.join(msg), withdate=False)


def interpret_state(state, obj):
    """return a string corresponding to the state name corresponding to `state'
    for a given sctp object `obj' (assoc_change, paddr_change, paddrinfo, status)
    """
    for state_name in [k for k in obj.__dict__ if k.startswith('state_')]:
        state_val = getattr(obj, state_name)
        if state == state_val:
            return state_name[6:]
    return '_unknown_'


def interpret_error(error, obj):
    """return a string corresponding to the error name corresponding to `error'
    for a given sctp object `obj' (assoc_change, paddr_change)
    """
    for err_name in [k for k in obj.__dict__ if k.startswith('error_')]:
        err_val = getattr(obj, err_name)
        if error == err_val:
            return err_name[6:]
    return '_unknown_'


def get_addr_fam(addrs):
    af_all = []
    for addr in addrs:
        if addr.count('.') == 3:
            af = AF_INET
            af_all.append(af)
        elif addr.count(':'):
            af = AF_INET6
            af_all.append(af)
        else:
            err = addr
            af_all.append(None)
    if af_all.count(af) != len(af_all):
        log('multi-homing on both IPv4 and IPv6 not supported')
        return None
    elif None in af_all:
        log('invalid IP address %s' % err)
        return None
    else:
        return af

#------------------------------------------------------------------------------#
# SCTP echo server
#------------------------------------------------------------------------------#

def server_stream(addrs, port, running, m3ua_asphs=False):
    """SCTP echo server with TCP-style socket, running in an endless loop
    """
    af = get_addr_fam(addrs)
    if not af:
        return
    #
    sk = sctp.sctpsocket_tcp(af)
    sk.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    laddrs = [(addr, port) for addr in addrs]
    sk.bindx(laddrs)
    #
    sk.set_sndbuf(SCTP_WMAX)
    sk.set_rcvbuf(SCTP_RMAX)
    if SCTP_MAXSEG:
        sk.set_maxseg(SCTP_MAXSEG)
    #
    # set proper events to be received and get notified for
    sk_set_events(sk)
    #
    sk.listen(SRV_MAXCLI)
    sk_list = [sk]
    log('Listening with TCP-style SCTP socket on %r' % laddrs)
    log_sockinfos(sk)
    #
    while running.is_set():
        skr = select(sk_list, [], [], SCTP_SELTO)[0]
        if not skr:
            continue
        #
        log('select(), fd ready: %s' % ', '.join(map(str, [s.fileno() for s in skr])))
        if sk in skr:
            # new client connecting
            cli, addr = sk.accept()
            log('Connected from %r, fd %i' % (addr, cli.fileno()))
            log_sockinfos(cli)
            sk_list.append(cli)
            skr.remove(sk)
        #
        for cli in skr:
            # existing connected client sending us a msg
            try:
                addr, flags, buf, notif = cli.sctp_recv(SCTP_RMAX)
            except (TimeoutError, ConnectionError) as err:
                if hasattr(cli, 'assoc_id'):
                    cli_id = 'fd %i, %r' % (cli.fileno(), cli.getpaddrs())
                else:
                    cli_id = 'fd %i' % cli.fileno()
                log('sctp_recv() exception from %s: %r' % (cli_id, err))
                cli.close()
                sk_list.remove(cli)
                continue
            else:
                if addr is not None:
                    cli_id = 'fd %i, %r' % (cli.fileno(), addr)
                else:
                    cli_id = 'fd %i' % cli.fileno()
            #
            # check for flags, notifications and association closing
            if flags & sctp.FLAG_DONTROUTE:
                log('SCTP flag DONTROUTE set by %s' % cli_id)
            if flags & sctp.FLAG_NOTIFICATION:
                # when notification flag is set, not data msg should be there
                assert( not buf )
                log('SCTP notification from %s: type %i, flags %i, %r' % (
                    cli_id, notif.type, notif.flags, notif))
                log_notifinfos(notif)
            elif not buf:
                # no notification neither buffer received is the way to indicate 
                # the endpoint closed the socket for TCP-style socket
                log('Disconnected from %s' % cli_id)
                cli.close()
                sk_list.remove(cli)
            #
            else:
                # data msg is there
                # sndrcvinfo is available within notif
                if not flags & sctp.FLAG_EOR:
                    log('Truncated buffer received from %s' % cli_id)
                log('Received %i bytes buffer from %s: PPID %i, stream %i' % (
                    len(buf), cli_id, ntohl(notif.ppid), notif.stream))
                #
                # echoing the received buffer to the client
                if len(buf) > SCTP_WMAX:
                    log('Warning: trying to send buffer longer than WMAX')
                if m3ua_asphs and buf[:2] == b'\x01\x00':
                    if buf[2] == 0x03:
                        log('M3UA ASP Up-Down-Beat handshake')
                        # M3UA ASP Up-Down-Beat
                        buf = buf[:3] + bytes([buf[3] + 3]) + buf[4:]
                    elif buf[2] == 0x04:
                        log('M3UA ASP Activate-Inactivate handshake')
                        # M3UA ASP Activate-Inactivate
                        buf = buf[:3] + bytes([buf[3] + 2]) + buf[4:]
                try:
                    ret = cli.sctp_send(buf, ppid=notif.ppid, stream=notif.stream)
                except Exception as err:
                    log('sctp_send() exception with %s: %r' % (cli_id, err))
                else:
                    log('Echoed buffer to %s: 0x%s' % (cli_id, hexlify(buf).decode()))
        #
        sleep(SCTP_SELTO)
    #
    sk.close()
    return 0


def server_dgram(addrs, port, running, m3ua_asphs=False):
    """SCTP echo server with UDP-style socket, running in an endless loop
    """
    af = get_addr_fam(addrs)
    if not af:
        return
    #
    sk = sctp.sctpsocket_udp(af)
    sk.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    laddrs = [(addr, port) for addr in addrs]
    sk.bindx(laddrs)
    #
    sk.set_sndbuf(SCTP_WMAX)
    sk.set_rcvbuf(SCTP_RMAX)
    if SCTP_MAXSEG:
        sk.set_maxseg(SCTP_MAXSEG)
    #
    # set proper events to be received and get notified for
    sk_set_events(sk)
    #
    sk.listen(SRV_MAXCLI)
    sk_list = [sk]
    log('Listening with UDP-style SCTP socket on %r' % laddrs)
    log_sockinfos(sk)
    #
    while running.is_set():
        skr = select(sk_list, [], [], SCTP_SELTO)[0]
        if not skr:
            continue
        #
        log('select(), fd ready: %s' % ', '.join(map(str, [s.fileno() for s in skr])))
        assert( skr[0] == sk )
        #
        # msg available straight from the server socket
        try:
            addr, flags, buf, notif = sk.sctp_recv(SCTP_RMAX)
        except (TimeoutError, ConnectionError) as err:
            # from there, I don't know how to get info about the peer
            log('sctp_recv() exception: %r' % err)
            continue
        else:
            if addr is not None:
                cli_id = 'assoc %i, %r' % (notif.assoc_id, addr)
                log('Receiving data or event from %s' % cli_id)
            else:
                cli_id = 'assoc %i' % notif.assoc_id
                log('Receiving data or event from %s: warning, no address available' % cli_id)
        #
        # check for flags, notifications and association closing
        if flags & sctp.FLAG_DONTROUTE:
            log('SCTP flag DONTROUTE set by %s' % cli_id)
        if flags & sctp.FLAG_NOTIFICATION:
            # when notification flag is set, not data msg should be there
            assert( not buf )
            log('SCTP notification from %s: type %i, flags %i, %r' % (
                cli_id, notif.type, notif.flags, notif))
            log_notifinfos(notif)
        elif not buf:
            # no notification neither buffer received is the way to indicate 
            # the endpoint closed the socket for TCP-style socket
            log('Disconnected from %s' % cli_id)
        #
        elif addr:
            # addr is required this time
            # data msg is there
            # sndrcvinfo is available within notif
            if not flags & sctp.FLAG_EOR:
                log('Truncated buffer received from %s' % cli_id)
            log('Received %i bytes buffer from %s' % (len(buf), cli_id))
            log_sndrcvinfo(notif)
            #
            # echoing the received buffer to the client
            if len(buf) > SCTP_WMAX:
                log('Warning: trying to send buffer longer than WMAX')
            if m3ua_asphs and buf[:2] == b'\x01\x00':
                if buf[2] == 0x03:
                    log('M3UA ASP Up-Down-Beat handshake')
                    # M3UA ASP Up-Down-Beat
                    buf = buf[:3] + bytes([buf[3] + 3]) + buf[4:]
                elif buf[2] == 0x04:
                    log('M3UA ASP Activate-Inactivate handshake')
                    # M3UA ASP Activate-Inactivate
                    buf = buf[:3] + bytes([buf[3] + 2]) + buf[4:]
            try:
                ret = sk.sctp_send(buf, to=addr, ppid=notif.ppid, stream=notif.stream)
            except Exception as err:
                log('sctp_send() exception with %s: %r' % (cli_id, err))
            else:
                log('Echoed buffer to %s: 0x%s' % (cli_id, hexlify(buf).decode()))
        #
        sleep(SCTP_SELTO)
    #
    sk.close()
    return 0


def main():
    parser = argparse.ArgumentParser(description='SCTP echo server')
    parser.add_argument('addrs', type=str, nargs='+', help='local address(es) to bind on')
    parser.add_argument('port', type=int, help='port to bind on')
    parser.add_argument('-u', action='store_true', help='run the SCTP server socket in UDP-style instead of TCP-style')
    parser.add_argument('-m', action='store_true', help='support very basically M3UA ASP handshakes in responses')
    args = parser.parse_args()
    #
    running = Event()
    running.set()
    try:
        if args.u:
            server_dgram(args.addrs, args.port, running, args.m)
        else:
            server_stream(args.addrs, args.port, running, args.m)
    except KeyboardInterrupt:
        log('CTRL+C: stopping')
        running.clear()
        sleep(SCTP_SELTO+0.01)
    #
    return 0


if __name__ == '__main__':
    sys.exit(main())

