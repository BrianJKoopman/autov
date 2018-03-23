# Brian Koopman
"""Explore how decentering the secondary changes the agreement of modeling with
observed planet positions."""

# Usage: python explore.py [ARRAY] [FREQ]

import time
import argparse
import logging
import numpy as np

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

def explore_decenter_parameter_space(decenter_parameter, values):
    for _value in values:
        print _value
        # Build .seq file for automated run.
        TEL = autoact.AutoACT(ARRAY, descriptors=["secondary_decentering", "pa%s"%(ARRAY), decenter_parameter, _value])
        TEL.create_header()
        TEL.load_clean_len()
        TEL.remove_glass()
        TEL.apply_ar_coatings()
        TEL.set_wavelengths(wavelengths=[int(autov.freq2lambda(int(args.frequency)))], reference=0)
    
        # surface 4 is the secondary
        TEL.set_decenter_type(4, 'decenter and return')
        TEL.decenter_surface(4, decenter_parameter, _value)
    
        TEL.set_fields(polarization=1)
        TEL.set_vignetting()
        TEL.activate_pol_ray_trace()
        TEL.set_image_semi_aperture()
        TEL.run_psf()
        TEL.run_real_ray_trace()
    
        # skipping polarization analysis, since it'll just slow us down for now
        #TEL.run_poldsp(input_angle=0, pupil_number=23)
        #TEL.run_poldsp(input_angle=90, pupil_number=23)
    
        TEL.exit()
        TEL.run()
        file_name = TEL.save_cfg(out_dir="./output/")


# alpha
explore_decenter_parameter_space('alpha', np.arange(-0.17, 0.17, 0.01))

# beta
explore_decenter_parameter_space('beta', np.arange(-0.17, 0.17, 0.01))

# x
explore_decenter_parameter_space('x', np.arange(-0.9, 1, 0.1))

# y
explore_decenter_parameter_space('y', np.arange(-0.9, 0.7, 0.1))

# z
explore_decenter_parameter_space('z', np.arange(-1.6, 2.0, 0.1))
