# Brian Koopman
"""Explore how decentering the secondary changes the agreement of modeling with
observed planet positions."""

# Usage: python explore.py [ARRAY] [FREQ]

import time
import argparse
import logging

from autov import autoact
from autov import autov

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['1', '2', '3', '4', '5', '6'], help="Array you want to automate.")
parser.add_argument("frequency", help="Frequency to run the Code V calculations at in units of GHz.")
args = parser.parse_args()

# Setup logging
logging.basicConfig(filename='./explore.log', format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w', level=logging.DEBUG)
logging.debug("Logging started.")

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"

# Build .seq file for automated run.
TEL = autoact.AutoACT(ARRAY, descriptors=["secondary_decentering", "pa%s"%(ARRAY)])
TEL.create_header()
TEL.load_clean_len()
TEL.remove_glass()
TEL.apply_ar_coatings()
TEL.set_wavelengths(wavelengths=[int(autov.freq2lambda(int(args.frequency)))], reference=0)

TEL.set_decenter_type(4, 'decenter and return')
TEL.decenter_surface(4, 'alpha', 0.1)

TEL.set_fields(polarization=1)
TEL.set_vignetting()
TEL.activate_pol_ray_trace()
TEL.set_image_semi_aperture()
#TEL.run_psf()
#TEL.run_real_ray_trace()
##TEL.run_poldsp(input_angle=0, pupil_number=23)
##TEL.run_poldsp(input_angle=90, pupil_number=23)
TEL.exit()
TEL.run()
TEL.save_cfg(out_dir="../output/secondary_decentering_exploration/")
