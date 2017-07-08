# Brian Koopman
"""Create polarization calibration Code V outputs for ar4."""

# Usage: python polcal_ar4.py [ARRAY] [FREQ]

import time
import argparse

from autov import autoact
from autov import autov

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['4'], help="Array you want to automate.")
parser.add_argument("frequency", help="Frequency to run the Code V calculations at in units of GHz.")
args = parser.parse_args()

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"

coating, descriptors = (r"E:\ownCloud\optics\mul\hf\three_layer_coating_120_185_285.mul", ["calibration", "pa%s"%(ARRAY)])

# Build .seq file for automated run.
arc_autov = autoact.AutoACT(ARRAY, descriptors)
arc_autov.create_header()
arc_autov.load_clean_len()
arc_autov.remove_glass()
arc_autov.enter_single_command('THC S47  100') # freeze focal plane
arc_autov.enter_single_command('CCY S45  100') # freeze l3_b y-radius
arc_autov.enter_single_command('CCY S41  100') # freeze l3_b y-radius
arc_autov.apply_ar_coatings(coating_file=coating)
if ARRAY in ['4']:
    arc_autov.set_wavelengths(wavelengths=[2070000, 1380000, 1130000, int(autov.freq2lambda(args.frequency))], reference=3) # ar4
else:
    raise ValueError("Array %s not yet supported."%(ARRAY))
arc_autov.set_fields(polarization=1)
arc_autov.set_vignetting()
arc_autov.activate_pol_ray_trace()
arc_autov.set_image_semi_aperture()
arc_autov.run_psf()
arc_autov.run_real_ray_trace()
arc_autov.run_poldsp(input_angle=0, pupil_number=23)
arc_autov.run_poldsp(input_angle=90, pupil_number=23)
arc_autov.exit()
arc_autov.run()
arc_autov.save_cfg(out_dir="../output/calibration/")
