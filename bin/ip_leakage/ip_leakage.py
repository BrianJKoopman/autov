# Brian Koopman
"""Explore I->P leakage in the ACTPol optical design."""
# Basically runs everything we do for polarization calibration, but with an
# input polarization fraction of 0, as opposed to 1. The amount of polarization
# on the focal plane is then the amount leaked from I->P.

# Usage: python ip_leakage.py [ARRAY] [FREQ]

import time
import argparse

from autov import autoact
from autov import autov

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['1', '2', '3', '4', '5', '6'], help="Array you want to automate.")
parser.add_argument("frequency", help="Frequency to run the Code V calculations at in units of GHz.")
parser.add_argument("-V", "--view", help="View only. Don't run the analysis steps, or save any cfg files. Will cause Code V not to exit after setup.", action="store_false")
args = parser.parse_args()

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"

# Build .seq file for automated run.
qq = autoact.AutoACT(ARRAY, descriptors=["ip_leakage", "pa%s"%(ARRAY)])
qq.create_header()
qq.load_clean_len()
qq.remove_glass()
qq.apply_ar_coatings()
qq.set_wavelengths(wavelengths=[int(autov.freq2lambda(int(args.frequency)))], reference=0)
qq.set_fields(polarization=0)
qq.set_vignetting()
qq.activate_pol_ray_trace()
qq.set_image_semi_aperture()

if args.view:
    qq.run_psf()
    qq.run_real_ray_trace()
    qq.run_poldsp(input_angle=0, pupil_number=23)
    qq.run_poldsp(input_angle=90, pupil_number=23)
    qq.exit()

qq.run()

if args.view:
    qq.save_cfg(out_dir="../output/ip_leakage/")
