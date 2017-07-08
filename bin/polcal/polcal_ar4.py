# To run a single wavelength and test for difference without Quick Best Focus.

import subprocess
import time
import argparse
from modules import autov

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['1', '2', '3', '4'], help="Array you want to automate.")
args = parser.parse_args()

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"

coating, descriptors = (r"E:\ownCloud\optics\mul\hf\three_layer_coating_120_185_285.mul",["HF"])

# Set ref_wl for file descriptors.
if ARRAY in ['4']:
    ref_wl = 2070000
else:
    raise ValueError("Array %s not yet supported."%(ARRAY))

# Build .seq file for automated run.
arc_autov = autov.AutoV(ARRAY, descriptors)
arc_autov.create_header()
arc_autov.load_clean_len()
arc_autov.remove_glass()
arc_autov.enter_single_command('THC S47  100') # freeze focal plane
arc_autov.enter_single_command('CCY S45  100') # freeze l3_b y-radius
arc_autov.enter_single_command('CCY S41  100') # freeze l3_b y-radius
arc_autov.apply_ar_coatings(coating_file = coating)
if ARRAY in ['4']:
    arc_autov.set_wavelengths(wavelengths=[2070000, 1380000, 1130000], reference=0) # ar1, ar2
else:
    #arc_autov.set_wavelengths(wavelengths=[3000000, 2070000, 1380000], reference=0) # ar3
    raise ValueError("Array %s not yet supported."%(ARRAY))
arc_autov.set_fields()
arc_autov.set_vignetting()
arc_autov.activate_pol_ray_trace()
arc_autov.set_image_semi_aperture()
arc_autov.run_psf()
arc_autov.run_real_ray_trace()
arc_autov.run_poldsp(input_angle=0, pupil_number=23)
arc_autov.run_poldsp(input_angle=90, pupil_number=23)
arc_autov.exit()
arc_autov.run()
arc_autov.save_cfg()

