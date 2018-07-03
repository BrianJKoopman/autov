"""Test mueller matrix output from CODE V by computing final Stokes parameters
for comparison."""

import numpy as np
import argparse

import ahab

parser = argparse.ArgumentParser()
parser.add_argument("config", help="Pass in the config file.")
args = parser.parse_args()

cfg = ahab.cfg.read_cfg(args.config)

mmtab_file = cfg['codev_inputs']['mmtab']

with open("/home/koopman/lab/optics/data/" + mmtab_file, 'r') as f:
    contents = f.readlines()

total_length = len(contents)
header = 12 # skip 12 lines in header
footer = 3

matricies = []
i = 0
for line in contents:
    if i < header:
        i+=1
        continue
    elif i >= len(contents)-footer:
        break
    else:
        matrix = np.array([contents[i].split()[1:5], contents[i+1].split(), contents[i+2].split(), contents[i+3].split()], dtype='float')
        matricies.append(matrix)
        i+=4
