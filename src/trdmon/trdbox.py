#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
#
# """

# import basesvc
import urwid
import pydim
import logging
from trdmon.dimwid import dimwid as dimwid
# from trdmon.basesvc import basesvc as basesvc

#
# class trdbox_daq_run(basesvc.basesvc):
#     def __init__(self):
#         super().__init__("trdbox/RUN_NUMBER", "I")
#
#     def refresh(self):
#         if self.value >= 0:
#             self.set_text(("fsm:ready", f"Run: {self.value:5d}"))
#         else:
#             self.set_text(("fsm:static", f"- no run -"))
#
# class trdbox_daq_bytes_read(basesvc.basesvc):
#     def __init__(self):
#         super().__init__("trdbox/DAQ/BYTES_READ", "I")
#
#     def refresh(self):
#         self.set_text(("bg", f"{self.value:9d} B"))
#

class trdbox_daq(urwid.Pile):
    def __init__(self):

        self.run = -999
        self.rd = 0
        self.wr = 0
        self.ev = 0

        self.w_run = urwid.Text("run")
        self.w_ev = urwid.Text("run")
        self.w_rd = urwid.Text("bytes R")

        super().__init__([
        urwid.Text("TRDbox : DAQ"),
        self.w_run, self.w_ev, self.w_rd])

        pydim.dic_info_service(f"trdbox/RUN_NUMBER", "I", self.cb_run)
        pydim.dic_info_service(f"trdbox/DAQ/EVENT_NUMBER", "I", self.cb_ev)
        pydim.dic_info_service(f"trdbox/DAQ/BYTES_WRITTEN", "I", self.cb_wr)
        pydim.dic_info_service(f"trdbox/DAQ/BYTES_READ", "I", self.cb_rd)

        dimwid.register_callback(self)

    def cb_run(self, x):
        self.run = x
        dimwid.request_callback(self)

    def cb_ev(self, x):
        self.ev = x
        dimwid.request_callback(self)

    def cb_wr(self, x):
        self.wr = x
        dimwid.request_callback(self)

    def cb_rd(self, x):
        self.rd = x
        dimwid.request_callback(self)

    def refresh(self):

        if self.run >= 0:
            self.w_run.set_text(("fsm:ready", f"Run: {self.run:5d}"))
        else:
            self.w_run.set_text(("fsm:static", f"- no run -"))

        self.w_ev.set_text(f"{self.ev:10d} events")
        self.w_rd.set_text(f"{self.rd:10d} bytes")


class trdbox_daq2(urwid.Pile):
    def __init__(self):

        super().__init__([
            # basesvc( "trdbox/RUN_NUMBER", "I", fmt = trdbox_daq2.fmt_run),
            # basesvc( "trdbox/RUN_NUMBER", "I", fmt = trdbox_daq2.fmt_run),
            basesvc( "trdbox/DAQ/BYTES_READ", "I",
                     fmt = lambda x: ("bg",f"{x} B")),
            #          # fmt = lambda x: ("bg",f"{float(x)/1024.:5f} kB")),
            # trdbox_daq_run()
        ])

    def fmt_run(runno):
        if runno >= 0:
            return ("fsm:ready", f"Run: {runno:5d}")
        else:
            return ("fsm:static", f"- no run -")
