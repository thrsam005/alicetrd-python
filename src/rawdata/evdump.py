#!/usr/bin/env python3
#

# import sys
# import zmq
# import numpy as np
# import argparse
# from struct import unpack
# import time
import click
import logging
from pprint import pprint

from .header import TrdboxHeader
from .linkparser import LinkParser, logflt
from .logging import ColorFormatter
# from .logging import AddLocationFilter
from .o32reader import o32reader
from .zmqreader import zmqreader

# create logger with 'spam_application'
logger = logging.getLogger(__name__)

# # create console handler with a higher log level
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)

# ch.setFormatter(CustomFormatter())
# logger.addHandler(ch)


@click.command()
@click.argument('source', default='tcp://localhost:7776')
@click.option('-o', '--loglevel', default=logging.INFO)
def evdump(source, loglevel):


    ch = logging.StreamHandler()
    ch.setFormatter(ColorFormatter())
    logging.basicConfig(level=loglevel, handlers=[ch])

    # Modify settings of the log filter
    logflt.dword_types['ADC']['suppress'] = True
    logflt.dword_types['MSK']['suppress'] = True
    logflt.dword_types['MCM']['suppress'] = True

    # logging.getLogger("rawdata.linkparser").setLevel(logging.INFO)
    # logging.getLogger("rawdata.linkparser").addHandler(ch)
    # logger.setLevel(loglevel)

    # headwords = 8 #20000
    # tailwords = 4 #10000
    # headwords = 20
    # tailwords = 10
    #
    # # equipments = [ 0x11, 0x21 ] # SFP1 - raw fragments and subevents
    # equipments = [0x10]
    # # equipments = None # None -> read all equipments
    #
    #


    # filename_format = "ev{evno:08d}_eq{eq:04}.npy"

    if source.endswith(".o32") or source.endswith(".o32.bz2"):
        reader = o32reader(source)

    elif source.startswith('tcp://'):
        reader = zmqreader(source)

    else:
        raise ValueError(f"unknown source type: {source}")


    # The actual reading is handled by the reader and the LinkParser

    lp = LinkParser()

    for event in reader:
        for subevent in event.subevents:
            lp.process(subevent.payload)
