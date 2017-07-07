# To run a single wavelength and test for difference without Quick Best Focus.

import subprocess
import time
import os
import argparse
import numpy as np

from autov import autoact

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['1', '2', '3'], help="Array you want to automate.")
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
if ARRAY in ['1', '2']:
    qq.set_wavelengths(wavelengths=[2140000, 2070000, 2000000], reference=1) # ar1, ar2
elif ARRAY in ['3']:
    qq.set_wavelengths(wavelengths=[3000000, 2070000, 1380000], reference=1) # ar3
qq.set_fields(polarization=0)
qq.set_vignetting()
qq.activate_pol_ray_trace()
qq.set_image_semi_aperture()
qq.run_psf()
qq.run_real_ray_trace()
qq.run_poldsp(input_angle=0, pupil_number=23)
qq.run_poldsp(input_angle=90, pupil_number=23)
qq.exit()
qq.run()
qq.save_cfg(out_dir="./output/calibration/")
