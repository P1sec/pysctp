# PYTHON_VERSION = 2.5
# When/if your favorite SCTP kernel impl is at least draft 10 compliant
#CFLAGS = -Wall `python-config --cflags` -fPIC -DSCTP_DRAFT10_LEVEL -DDEBUG
# this is however not supported by recent kernel, e.g. some of the constants
# have been renamed / changed
#
# If not
CFLAGS = -Wall `python-config --cflags` -fPIC -DDEBUG

LDFLAGS = `python-config --ldflags` -fPIC -shared -lsctp

all: _sctp.so

clean:
	rm -f *.so *.o *.pyc
	rm -fr build/temp.*
	rm -fr build/lib.*
	rm -f dist/*

_sctp.so: _sctp.o
	gcc $(LDFLAGS) -o _sctp.so _sctp.o

_sctp.o: _sctp.c
	gcc $(CFLAGS) -c _sctp.c

installdeps:
	sudo apt-get install libsctp-dev python-dev
