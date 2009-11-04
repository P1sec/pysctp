"""
setup.py

Created by Philippe Langlois on 2009-11-02.
Copyright (c) 2009 Philippe Langlois. All rights reserved.
"""

from distutils.core import setup, Extension

setup(name='pysctp',
      version='0.5',
      license = "LGPL",
      description = 'pysctp is a python module for the SCTP protocol stack and library. ',
      long_description = 'pysctp is a python module for the SCTP protocol stack and library. It is the socket api implementation, not the SCTPlib implementation (this latest one is not supported anymore by their original developers). On Mac OS X you will need the SCTP NKE (Kernel Extensions) to make it work, use: http://sctp.fh-muenster.de/sctp-nke.html. On Debian-based systems, you need a SCTP-aware kernel (most are) and install the following packages: apt-get install libsctp-dev libsctp1 lksctp-tools',
      url = "http://www.epx.com.br/pysctp/",
      keywords = "SCTP SIGTRAN",
      platforms = ["Linux", "Debian", "Ubuntu", "Mac OS X (tested on 10.4)"],
      classifiers = [ 'Development Status :: 4 - Beta',
                      'Intended Audience :: Developers',
                      'License :: OSI Approved :: LGPL License',
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
	  data_files=['_sctp.h'],
	  author='Elvis Pfutzenreuter',
	  author_email='epx@epx.com.br',
      maintainer='Philippe Langlois',
 	  maintainer_email='Philippe.Langlois@gmail.com',
      )
