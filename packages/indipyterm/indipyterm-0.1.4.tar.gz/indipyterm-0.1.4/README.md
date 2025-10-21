# indipyterm

This indipyterm package provides a terminal client, which connects to an INDI server, allowing you to view and control your instrument from a terminal session.

INDI defines a protocol for the remote control of instruments.

INDI - Instrument Neutral Distributed Interface.

See https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

The INDI protocol defines the format of the data sent, such as light, number, text, switch or BLOB (Binary Large Object). The client is general purpose, taking the format of switches, numbers etc., from the protocol.

indipyterm can be installed from Pypi:

https://pypi.org/project/indipyterm

Or if you use uv, it can be loaded and run with:

uvx indipyterm

The client is typically run from a virtual environment with

indipyterm [options]

or with

python3 -m indipyterm [options]

The package help is:

    usage: indipyterm [options]

    Terminal client to communicate to an INDI service.

    options:
      -h, --help               show this help message and exit
      --port PORT              Port of the INDI server (default 7624).
      --host HOST              Hostname/IP of the INDI server (default localhost).
      --blobfolder BLOBFOLDER  Optional folder where BLOB's will be saved.

      --version    show program's version number and exit

A typical session would look like:

![Terminal screenshot](https://github.com/bernie-skipole/indipyterm/raw/main/indipyterm1.png)

and showing one device:

![Terminal screenshot](https://github.com/bernie-skipole/indipyterm/raw/main/indipyterm2.png)


This terminal should work with any INDI service, however associated packages by the same author are:

## indipyserver

https://github.com/bernie-skipole/indipyserver

https://pypi.org/project/indipyserver/

https://indipyserver.readthedocs.io

## indipydriver

https://github.com/bernie-skipole/indipydriver

https://pypi.org/project/indipydriver

https://indipydriver.readthedocs.io
