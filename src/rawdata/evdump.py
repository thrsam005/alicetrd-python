#!/usr/bin/env python3
#

import sys
import zmq
import numpy as np
import argparse
from struct import unpack
import time

from .header import TrdboxHeader

def evdump():

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

    while True:
        rawdata = socket.recv()
        evno += 1

        print("-------------------------------------------------------------")
        header = TrdboxHeader(rawdata)
        print(header, end="")

        # print("-------------------------------------------------------------")
        payload = np.frombuffer(rawdata[header.header_size:], dtype=np.uint32)

        if filename_format is not None:
            vars = dict(evno=evno, eq=header.equipment())
            with open(filename_format.format(**vars), "wb") as f:
                np.save(f, payload)


        if len(payload)<(headwords+tailwords):
            for i,x in enumerate(payload):
                print(f"{i:06x} {x:08x}")

        else:
            for i,x in enumerate(payload[:headwords]):
                print(f"{i:06x} {x:08x}")
            print("...")
            for i,x in enumerate(payload[-tailwords:], start=len(payload)-tailwords):
                print(f"{i:06x} {x:08x}")
