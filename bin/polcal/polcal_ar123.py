# Brian Koopman
"""Create polarization calibration Code V outputs for ar1, ar2 and ar3."""

# Usage: python polcal_ar123.py [ARRAY] [FREQ]

import time
import argparse

from autov import autoact
from autov import autov

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['1', '2', '3'], help="Array you want to automate.")
parser.add_argument("frequency", help="Frequency to run the Code V calculations at in units of GHz.")
args = parser.parse_args()

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"

# Build .seq file for automated run.
qq = autoact.AutoACT(ARRAY, descriptors=["calibration", "pa%s"%(ARRAY)])
qq.create_header()
qq.load_clean_len()
qq.remove_glass()
qq.apply_ar_coatings()
# There's some sublte difficulty in setting wavelengths, the first three here are assumed to be already set in a clean file.
# We just set to the passed in frequency and use that as a reference.
if ARRAY in ['1', '2']:
    qq.set_wavelengths(wavelengths=[2140000, 2070000, 2000000, int(autov.freq2lambda(args.frequency))], reference=3) # ar1, ar2
elif ARRAY in ['3']:
    qq.set_wavelengths(wavelengths=[3000000, 2070000, 1380000, int(autov.freq2lambda(args.frequency))], reference=3) # ar3
qq.set_fields(polarization=1)
qq.set_vignetting()
qq.activate_pol_ray_trace()
qq.set_image_semi_aperture()
qq.run_psf()
qq.run_real_ray_trace()
qq.run_poldsp(input_angle=0, pupil_number=23)
qq.run_poldsp(input_angle=90, pupil_number=23)
qq.exit()
qq.run()
qq.save_cfg(out_dir="../output/calibration/")
