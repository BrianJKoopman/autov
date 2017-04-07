# Test polarization angle change as tolerances are introduced. Trying to place
# uncertainty estiamte on polarization rotation.

import subprocess
import time
import argparse
import logging
import numpy as np
#from modules import autov
from autov import autoact

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['1', '2', '3', '4'], help="Array you want to automate.")
args = parser.parse_args()

# Setup logging
logging.basicConfig(filename='./log/dev.log', format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w', level=logging.DEBUG)
logging.info("Logging started.")

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"

# Set ref_wl for file descriptors.
if ARRAY in ['1', '2', '4']:
    ref_wl = 2070000
elif ARRAY in ['3']:
    ref_wl = 3000000

descriptors = []
# Build .seq file for automated run.
arc_autov = autoact.AutoACT(ARRAY, descriptors)
arc_autov.create_header()
arc_autov.load_clean_len()
#arc_autov.decenter_cryostat('y', 1)
arc_autov.perturb_lens_thickness(1, 0.5)
arc_autov.run()
