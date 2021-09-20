#!/usr/bin/env python3
#

import sys
import zmq
import numpy as np
import argparse
from struct import unpack
import time
import click
import logging

from .header import TrdboxHeader
from .linkparser import LinkParser
from .logging import ColorFormatter
from .logging import AddLocationFilter

# create logger with 'spam_application'
logger = logging.getLogger(__name__)

# # create console handler with a higher log level
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)

# ch.setFormatter(CustomFormatter())
# logger.addHandler(ch)


@click.command()
@click.option('-l', '--loglevel', default=logging.INFO)
def evdump(loglevel):


    ch = logging.StreamHandler()
    ch.setFormatter(ColorFormatter())
    logging.basicConfig(level=loglevel, handlers=[ch])


    # logging.getLogger("rawdata.linkparser").setLevel(logging.INFO)
    # logging.getLogger("rawdata.linkparser").addHandler(ch)
    # logger.setLevel(loglevel)

    # headwords = 8 #20000
    # tailwords = 4 #10000
    headwords = 20
    tailwords = 10

    # equipments = [ 0x11, 0x21 ] # SFP1 - raw fragments and subevents
    equipments = [0x10]
    # equipments = None # None -> read all equipments


    #  Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    print("Collecting updates from binary data server...")
    socket.connect("tcp://localhost:7776")

    # Subscribe to data feed
    magicbytes = np.array([0xDA7AFEED],dtype=np.uint32).tobytes()

    if equipments is None:
        socket.setsockopt(zmq.SUBSCRIBE, magicbytes)
    else:
        for eq in equipments:
            filter = magicbytes + (eq).to_bytes(1,'little');
            socket.setsockopt(zmq.SUBSCRIBE, filter)

    evno = -1
    filename_format = "ev{evno:08d}_eq{eq:04}.npy"

    lp = LinkParser()


    while True:
        rawdata = socket.recv()
        evno += 1

        print("-------------------------------------------------------------")
        header = TrdboxHeader(rawdata)
        print(header, end="")

        # print("-------------------------------------------------------------")
        payload = np.frombuffer(rawdata[header.header_size:], dtype=np.uint32)

        # if filename_format is not None:
        #     vars = dict(evno=evno, eq=header.equipment())
        #     with open(filename_format.format(**vars), "wb") as f:
        #         np.save(f, payload)
        #


        lp.process(payload)
