#!/usr/bin/env python3

import numpy as np

from rawdata import LinkParser
import rawdata

rawdata.check_dword(0x0380c02b)



# with open("ev00000000_eq4097.npy", "rb") as f:
#     payload = np.load(f)
#
# # print(payload)
# lp = LinkParser()
#
# lp.process(payload)
