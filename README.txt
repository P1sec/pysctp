PySCTP - SCTP bindings for Python
---------------------------------

Elvis Pfützenreuter 
Instituto Nokia de Tecnologia (http://www.indt.org.br)
epxx __AT__ epxx.co

Philippe Langlois
P1 Security (https://www.p1sec.com)
phil __AT__ p1sec.com

Benoit Michau
P1 Security
benoit.michau __AT__ p1sec.com


======================================================================
INSTALL

sudo python setup.py install

* to see what this is going to install without actually doing it:
python setup.py install --dry-run

* to just build and not install:
python setup.py build

In case you want to install the module explicitely for Python 2 or 3,
just replace _python_ by _python2_ / _python3_ in the commands above.

A pre-built package is also available for Python3 for the common Linux 
distributions:
pip install pysctp

The _Makefile_ available was used when installing with very old versions
of Python (2.5, 2.6...), and is not required anymore for building the package
with a recent Python (Python 3.6, 3.7...).


======================================================================
DEPENDENCIES:

When building the project, the following dependencies are required e.g.
on Debian / Ubuntu: libsctp-dev and python-dev
(python2-dev or python3-dev for an explicit version of Python)

You can automatically install dependencies for Debian / Ubuntu:
make installdeps
(take care with the Python version your are targeting, however)


======================================================================
INTRODUCTION

PySCTP gives access to the SCTP transport protocol from the Python language.
It wraps the Linux SCTP kernel API, and extends the traditional socket interface, 
allowing SCTP sockets to be used in most situations where a TCP or UDP socket
would work, while preserving the unique characteristics of the protocol.

For more information about SCTP, go to the IETF RFC 9260: https://www.rfc-editor.org/rfc/rfc9260
For discussion, sources, bugs, go to http://github.com/p1sec/pysctp

In a nutshell, PySCTP can be used as follows:

---------

import socket
import sctp

sk = sctp.sctpsocket_tcp(socket.AF_INET)
sk.connect(("10.0.1.1", 36413))

... most socket operations work for SCTP too ...

sk.close()

---------

The autotest programs (e.g. test_local_cnx.py) are actually good examples 
of pysctp usage. The SCTP echo server is also good for illustrating all the 
IO and events notifications available when dealing with SCTP.

The IETF RFC 6458 (https://www.rfc-editor.org/rfc/rfc6458.html) defines 
a POSIX API for SCTP sockets. The Linux API mostly follows it, but still
has some discrepancies in few cases. PySCTP targets the Linux API first,
and may support alternative implementations with few changes. This is however
untested.
The Linux API itself has slightly evolved and been extended (e.g. between 4.16 
and 4.17). Those "recent" changes are not reflected (yet) by PySCTP.


======================================================================
DESCRIPTION

1) The "sctp" module

The "sctp" module is the Python side of the bindings. The docstrings
of every class and method can give good advice of functions, but the
highlights are:

* sctpsocket is the root class for SCTP sockets, that ought not be used
  directly by the users. It does *not* inherit directly from Python
  standard socket; instead it *contains* a socket. That design was
  followed mostly because UDP-style sockets can be "peeled off" and 
  return TCP-style sockets. 

  sctpsocket delegates unknown methods to the socket. This ensures that
  methods like close(), bind(), read(), select() etc. will work as expected.
  If the real socket is really needed, it can be obtained with
  sctpsocket.sock().

* As said, "Normal" socket calls like open(), bind(), close() etc. 
  can be used on SCTP sockets because they are delegated to the
  Python socket. 

* Users will normally use the sctpsocket_tcp (TCP style) and sctpsocket_udp
  (UDP style) classes. Some calls that are implemented in sctpsocket but 
  do not make sense in a particular style are rendered invalid in each
  class (e.g. peeloff() in TCP-style sockets).

2) The "_sctp" module

This is the C side of the bindings, that provides the "glue" between
Python and the C API. The regular PySCTP user should not need to get 
into this, but power users and developers may be interested in it. 

The interface between Python and C is designed to be as simple as
possible. In particular, no object is created in C side, just 
simple types (strings, integers, lists, tuples and dictionaries).

The translation to/from complex objects is done entirely in Python.


======================================================================
Contributing

Any contributions is welcome, be it in terms of code, documentation or 
bug report.

When opening an issue, please indicate the detailed configuration of your 
environment: OS, kernel and Python versions, PySCTP commit or tagged version.
Provide also a detailed description of your issue, with a code extract
enabling to reproduce the issue, a pcap illustrating it, and more generally
as much possible information to help identify precisely the root cause
and solving it.


======================================================================
License

This module is licensed under the LGPL.
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html


======================================================================
History

The original PySCTP library was developed by Elvis Pfützenreuter (https://epxx.co/),
starting in 2005 / 2006. At that time, SCTP was freshly introduced into Linux, 
hence the library was developed targeting lksctp-utils 1.0.1 and kernel 2.6.10, 
that came with Ubuntu Hoary.

Since then, the kernel API evolved, and PySCTP too, in order to support newer
calls like connectx(). In 2009/2010, Philippe Langlois headed to maintain the 
library, which is now supported by the P1 Security team since then.
The Linux API has again slightly evolved in the last years, which changes are 
not (yet) reflected in PySCTP.


======================================================================
Credits

Elvis Pfützenreuter
Philippe Langlois
Casimiro Daniel NPRI (patch for new SCTP_* constants)
Domonkos P. Tomcsanyi and Aurelien Roose (pypi / github integration)
Benoit Michau

