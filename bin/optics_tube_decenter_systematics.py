# Test polarization angle change as tolerances are introduced. Trying to place
# uncertainty estiamte on polarization rotation.

#import subprocess
import time
import argparse
import logging
import numpy as np
from autov import autoact

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

def test_decenter(parameter, values, units):
    for value in values:
        if parameter in ['x', 'y', 'z']:
            descriptors = [parameter, "%smm"%(int(value*10))] # Note, this is done to avoid a decimal in the filename!
        else:
            descriptors = [parameter, "%sdeg"%(str(value).replace('.', 'p'))]
        # Build .seq file for automated run.
        arc_autov = autoact.AutoACT(ARRAY, descriptors)

        decenter_description_dict = {"type": "decenter", "parameter": parameter, "offset": value, "units": units}
        arc_autov.add_to_json_cfg("perturbation", decenter_description_dict)

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
        #arc_autov.run_poldsp(input_angle=90, pupil_number=23)

        arc_autov.exit()
        arc_autov.run()
        arc_autov.save_cfg(out_dir="./output/optics_tube/%s_decenter/"%(parameter))

# x, y, z decenters -1 to 1 cm
#parameter = "x"
#values = np.arange(-10,11)/10.
translation_values = np.linspace(-1, 1, 5)
test_decenter("x", translation_values, "cm")
test_decenter("y", translation_values, "cm")
test_decenter("z", translation_values, "cm")

# alpha, beta
#parameter = "alpha"
#tilt_values = np.arange(-20, 22, 2)/10. #-2 to 2 degrees in 0.2 deg steps
tilt_values = np.linspace(-2, 2, 5) # -2 to 2 degrees 
test_decenter("alpha", tilt_values, "deg")
test_decenter("beta", tilt_values, "deg")
