#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

# import sys
import time
# import curses
import urwid


from trdmon.dimwid import dimwid as dimwid
# import proc
# import dimmon
import pydim
import trdmon.trdbox as trdbox
import logging
import json
import os
import struct
from pprint import pprint
import functools

logging.basicConfig(filename='/tmp/trdmon.log', level=logging.DEBUG,
          format='%(asctime)s %(levelname)s %(funcName)s: %(message)s')
logger=logging.getLogger(__name__)

# # def subscr(cl, name, desc):
# #     org_init = cl.__init__
# #
# #     # Enhance the class to store the creation
# #     # time based on the instantiation.
# #     @functools.wraps(org_init)
# #     def new_init(self, *args, **kwargs):
# #         org_init(self, *args, **kwargs)
# #
# #
# #     # __lt__ and __gt__ methods return true or false
# #     # based on the creation time.
# #     cl.__init__ = new_init
# #     cl.cb = lambda self,x: self.val = x
# #     # cl.__lt = lambda self, other: self._created < other._created
# #     # cl.__gt__ = lambda self, other: self._created > other._created
# #     return cl
#
# class dimwid_t:
#
#     def __init__(self):
#         self.callbacks = dict()
#         self.pipefd = None
#
#     def register_callback(self, cb):
#         self.callbacks[id(cb)] = cb
#         # print(self.callbacks.keys())
#         # logger.debug(f"registering {id(cb)}")
#
#     def request_callback(self, cb):
#         if self.pipefd is not None:
#             os.write(self.pipefd, struct.pack("Q", id(cb)))
#
#     def receive_output(self, x):
#         for id in struct.iter_unpack("Q", x):
#             self.callbacks[id[0]].refresh()
#
#     def connect_loop(self, loop):
#         self.pipefd = loop.watch_pipe(self.receive_output)
#
# dimwid = dimwid_t()
#
#
#
#
# class bla(urwid.Text):
#
#     def __init__(self, dimname="example-service-1", timeout=10):
#         super().__init__("SERVICE 1")
#         pydim.dic_info_service(dimname, "C", self.dimcb, timeout)
#         dimwid.register_callback(self)
#
#         self.txt = "SERVICE 1"
#
#     def dimcb(self, x):
#         self.txt = x
#         dimwid.request_callback(self)
#
#     def refresh(self):
#         self.set_text(self.txt)
#
# class svc2(urwid.Text):
#
#     def __init__(self, name, desc=None, timeout=10):
#         super().__init__("SERVICE 2")
#         pydim.dic_info_service(name, self.dimcb, timeout)
#         dimwid.register_callback(self)
#         self.x = 0
#         self.y = 0
#
#     def dimcb(self, x,y):
#         self.x = x
#         self.y = y
#         dimwid.request_callback(self)
#
#     def refresh(self):
#         self.set_text(f"x={self.x} y={self.y}")
#         # self.set_text(f"x={x['x']} y={x['y']}")
#
# class basesvc(urwid.Text):
#
#     def __init__(self, name, desc=None, default=0, fmt=None, timeout=10):
#         super().__init__("---")
#         pydim.dic_info_service(name, desc, self.callback, timeout)
#         dimwid.register_callback(self)
#         self.value = default
#         self.format = fmt
#
#     def callback(self, x):
#         self.value = x
#         dimwid.request_callback(self)
#
#     def refresh(self):
#         if self.format is None:
#             self.set_text( str(self.value) )
#         elif callable(self.format):
#             self.set_text( self.format(self.value) )
#         else:
#             raise(ValueError(f"Unknown format type: {type(self.format)}"))
#
#         # self.set_text(f"x={self.x} y={self.y}")
#         # self.set_text(f"x={x['x']} y={x['y']}")
#
#
# class trdbox_daq_run(basesvc):
#     def __init__(self):
#         super().__init__("trdbox/RUN_NUMBER", "I")
#
#     def refresh(self):
#         if self.value >= 0:
#             self.set_text(("fsm:ready", f"Run: {self.value:5d}"))
#         else:
#             self.set_text(("fsm:static", f"- no run -"))
#
# class trdbox_daq_bytes_read(basesvc):
#     def __init__(self):
#         super().__init__("trdbox/DAQ/BYTES_READ", "I")
#
#     def refresh(self):
#         self.set_text(("bg", f"{self.value:9d} B"))
#
#
#
# class trdbox_daq(urwid.Pile):
#     def __init__(self):
#
#         self.run = -999
#         self.rd = 0
#         self.wr = 0
#         self.ev = 0
#
#         self.w_run = urwid.Text("run")
#         self.w_ev = urwid.Text("run")
#         self.w_rd = urwid.Text("bytes R")
#
#         super().__init__([self.w_run, self.w_ev, self.w_rd])
#
#         pydim.dic_info_service(f"trdbox/RUN_NUMBER", "I", self.cb_run)
#         pydim.dic_info_service(f"trdbox/DAQ/EVENT_NUMBER", "I", self.cb_ev)
#         pydim.dic_info_service(f"trdbox/DAQ/BYTES_WRITTEN", "I", self.cb_wr)
#         pydim.dic_info_service(f"trdbox/DAQ/BYTES_READ", "I", self.cb_rd)
#
#         dimwid.register_callback(self)
#
#     def cb_run(self, x):
#         self.run = x
#         dimwid.request_callback(self)
#
#     def cb_ev(self, x):
#         self.ev = x
#         dimwid.request_callback(self)
#
#     def cb_wr(self, x):
#         self.wr = x
#         dimwid.request_callback(self)
#
#     def cb_rd(self, x):
#         self.rd = x
#         dimwid.request_callback(self)
#
#     def refresh(self):
#
#         if self.run >= 0:
#             self.w_run.set_text(("fsm:ready", f"Run: {self.run:5d}"))
#         else:
#             self.w_run.set_text(("fsm:static", f"- no run -"))
#
#         self.w_ev.set_text(f"{self.ev:10d} events")
#         self.w_rd.set_text(f"{self.rd:10d} bytes")
#
#
# class trdbox_daq2(urwid.Pile):
#     def __init__(self):
#
#         super().__init__([
#             # basesvc( "trdbox/RUN_NUMBER", "I", fmt = trdbox_daq2.fmt_run),
#             # basesvc( "trdbox/RUN_NUMBER", "I", fmt = trdbox_daq2.fmt_run),
#             basesvc( "trdbox/DAQ/BYTES_READ", "I",
#                      fmt = lambda x: ("bg",f"{x} B")),
#             #          # fmt = lambda x: ("bg",f"{float(x)/1024.:5f} kB")),
#             # trdbox_daq_run()
#         ])
#
#     def fmt_run(runno):
#         if runno >= 0:
#             return ("fsm:ready", f"Run: {runno:5d}")
#         else:
#             return ("fsm:static", f"- no run -")
#
#


class rocstate(urwid.AttrMap): #(urwid.Text("FOO"),"state")):

    def __init__(self, sm,stack,layer):
        self.textwidget = urwid.Text(("state", "SERVICE 2"))
        super().__init__(self.textwidget, {"state": "state"} )
        # super().__init__(self.textwidget, {"fsm:undef": "fsm:undef"})
        pydim.dic_info_service(f"trd-fee_{sm:02d}_{stack}_{layer}_STATE",
                               "I", self.dimcb, timeout=30)
        dimwid.register_callback(self)
        self.state = -999
        self.statemap = {
          -999: "off",
          0: "off",
          13: "ERROR",
          99: "ERROR",
          5: "STANDBY",
          43: "STDBY_INIT",
          3: "CONFIGURED",
          42: "INITIALIZING",
          44: "CONFIGURING",
          45: "TESTING" }

    def dimcb(self, s):
        self.state = s
        dimwid.request_callback(self)

    def refresh(self):

        if self.state in [ -999, 0]:
            self.textwidget.set_text(("fsm:off", "off"))

        elif self.state in [ 13, 99 ]:
            self.textwidget.set_text(("fsm:error", "ERROR"))

        elif self.state == 5:
            self.textwidget.set_text(("fsm:static", "STANDBY"))

        elif self.state == 43:
            self.textwidget.set_text(("fsm:static", "STANDBY_INIT"))

        elif self.state == 3:
            self.textwidget.set_text(("fsm:ready", "CONFIGURED"))

        elif self.state == 42:
            self.textwidget.set_text(("fsm:trans", "INITIALIZING"))

        elif self.state == 44:
            self.textwidget.set_text(("fsm:trans", "CONFIGURING"))

        elif self.state == 45:
            self.textwidget.set_text(("fsm:trans", "TESTING"))

        else:
            self.textwidget.set_text(("fsm:error", f"state:{state:02X}"))


# ===========================================================================

def exit_on_enter(key):
    if key == 'enter': raise urwid.ExitMainLoop()

palette = [
    ('state', 'light green', 'black'),

    ('fsm:off',     'dark gray',  'black'),
    ('fsm:static',  'light blue', 'black'),
    ('fsm:ready',   'light green', 'black'),
    ('fsm:trans',   'yellow',     'black'),
    ('fsm:error',   'white',      'light red'),

    ('bg', 'light gray', 'black'),
    ('foo', 'light red', 'black'),
    ]

# output_widget = urwid.Text("BLA:\n")
whead = urwid.Text(("bg", "HEADER"))
# wsvc1 = urwid.Text("SERVICE 1")
top_widget = urwid.Frame(
    header=whead,
    body =
     urwid.AttrMap(urwid.Filler(urwid.Pile([
      rocstate(0,2,0),
      trdbox.trdbox_daq(),
      # trdbox_daq2(),
      # trdbox_daq_run(),
      # trdbox_daq_bytes_read(),
    ])), 'bg'),
    # body=urwid.Pile([bla()]),
    focus_part='header')

loop = urwid.MainLoop(top_widget, palette, unhandled_input=exit_on_enter)
dimwid.connect_loop(loop)

loop.run()
# proc.kill()
