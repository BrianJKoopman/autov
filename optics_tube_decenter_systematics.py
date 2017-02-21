# Test polarization angle change as tolerances are introduced. Trying to place
# uncertainty estiamte on polarization rotation.

import subprocess
import time
import argparse
import logging
import numpy as np
from modules import autov

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['1', '2', '3'], help="Array you want to automate.")
args = parser.parse_args()

# Setup logging
logging.basicConfig(filename='./log/optics_tube_decenter.log', format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w', level=logging.DEBUG)
logging.debug("Logging started.")

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"

parameter = "y"
values = np.arange(-10,11)/10.

def test_decenter(parameter, values):
    for value in values:
        # Set ref_wl for file descriptors.
        if ARRAY in ['1', '2']:
            ref_wl = 2070000
        elif ARRAY in ['3']:
            raise ValueError("Array 3 not yet supported.")
            #ref_wl = 3000000

        descriptors = [parameter, "%smm"%(int(value*10))]
        # Build .seq file for automated run.
        arc_autov = autov.AutoV(ARRAY, descriptors)
        arc_autov.create_header()
        arc_autov.load_clean_len()
        arc_autov.remove_glass()
        arc_autov.apply_ar_coatings()
        if ARRAY in ['1', '2']:
            arc_autov.set_wavelengths(wavelengths=[2140000, 2070000, 2000000], reference=1) # ar1, ar2
        elif ARRAY in ['3']:
            #arc_autov.set_wavelengths(wavelengths=[3000000, 2070000, 1380000], reference=0) # ar3
            raise ValueError("Array 3 not yet supported.")

        # Test
        arc_autov.decenter_cryostat(parameter, value)

        arc_autov.set_fields()
        arc_autov.set_vignetting()
        arc_autov.activate_pol_ray_trace()
        arc_autov.set_image_semi_aperture()

        # Setup to run tests in CODE V. These all need to be output to config files.
        arc_autov.run_psf()
        arc_autov.run_real_ray_trace()
        arc_autov.run_poldsp(input_angle=0, pupil_number=23)
        arc_autov.run_poldsp(input_angle=90, pupil_number=23)

        arc_autov.exit()
        arc_autov.run()
        arc_autov.save_cfg()

test_decenter(parameter, values)

# Old script before looping.
## Build .seq file for automated run.
#qq = autov.AutoV(ARRAY)
#qq.create_header()
#qq.load_clean_len()
#qq.remove_glass()
#qq.apply_ar_coatings(coating_file = r"E:\ownCloud\optics\mul\ar_coating_sys\two_layer_coating_138_m5_250_m5.mul")
#if ARRAY in ['1', '2']:
#    qq.set_wavelengths(wavelengths=[2140000, 2070000, 2000000], reference=1) # ar1, ar2
#    ref_wl = 2070000
#elif ARRAY in ['3']:
#    qq.set_wavelengths(wavelengths=[3000000, 2070000, 1380000], reference=0) # ar3
#    ref_wl = 3000000
#qq.set_fields()
#qq.set_vignetting()
#qq.activate_pol_ray_trace()
#qq.set_image_semi_aperture()
#qq.run_psf([str(int(ref_wl))])
#qq.run_real_ray_trace(file_descriptors=[str(int(ref_wl))])
#qq.run_poldsp(input_angle=0, file_descriptors=[str(int(ref_wl))], pupil_number=23)
#qq.run_poldsp(input_angle=90, file_descriptors=[str(int(ref_wl))], pupil_number=23)
#qq.exit()
#qq.run()
