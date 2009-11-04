PYTHON_VERSION = 2.5
CFLAGS = -Wall -I/usr/include/python$(PYTHON_VERSION) -I/Library/Frameworks/Python.framework/Versions/$(PYTHON_VERSION)/include/python$(PYTHON_VERSION) -fPIC
LDFLAGS = -fPIC -shared -lsctp

# When/if your favorite SCTP kernel impl is at least draft 10 compliant
# CFLAGS = $(CFLAGS) -DSCTP_DRAFT10_LEVEL

CFLAGS += -DDEBUG

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
