"""
setup.py

Created by Philippe Langlois on 2009-11-02.
Copyright (c) 2009 Philippe Langlois. All rights reserved.

This library is free software; you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation; either version 2.1 of the License, or (at your
option) any later version.

This library is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License
along with this library; If not, see <http://www.gnu.org/licenses/>.

"""

import setuptools
from distutils.core import setup, Extension

setup(name='pysctp',
      version='0.6.1',
      license = "LGPL",
      description = 'pysctp is a python module for the SCTP protocol stack and library. ',
      long_description = 'pysctp is a python module for the SCTP protocol stack and library. It is the socket API implementation, not the SCTPlib implementation (this latest one is not supported anymore by their original developers). On Mac OS X you will need the SCTP NKE (Kernel Extensions) to make it work, use: http://sctp.fh-muenster.de/sctp-nke.html. On Debian-based systems, you need a SCTP-aware kernel (most are) and install the following packages: apt-get install libsctp-dev libsctp1 lksctp-tools',
      url = "https://github.com/p1sec/pysctp",
      keywords = "SCTP SIGTRAN",
      platforms = ["Linux", "Debian", "Ubuntu", "Mac OS X (tested on 10.4)"],
      classifiers = ['Development Status :: 5 - Production/Stable',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                     'Programming Language :: C',
                     'Programming Language :: Python',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     'Topic :: System :: Networking' ],
      py_modules=['sctp'],
	  ext_modules=[Extension('_sctp', sources=['_sctp.c'],
	  						 include_dirs=['.', '/usr/include'],
	  						 libraries=['sctp'], 
	  						 library_dirs=['/usr/lib/', '/usr/local/lib/'],
							)
				  ],
	  data_files=[('include', ['_sctp.h'])],
	  author='Elvis Pfutzenreuter',
	  author_email='epx@epx.com.br',
      maintainer='Benoit Michau',
 	  maintainer_email='benoit.michau@p1sec.com',
      )
