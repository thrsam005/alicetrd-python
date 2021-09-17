#!/usr/bin/env python3

import numpy as np

from rawdata import LinkParser


with open("ev00000000_eq4097.npy", "rb") as f:
    payload = np.load(f)

# print(payload)
lp = LinkParser()

lp.process(payload)
