# Determine the effective change in the location of the cryotat to account for a decenter in the secondary. 
# Goals:
    ## Cut down surfaces to surface of the reciever as the image.
    ## Delete all fields except for chief ray.
    ## set decenter and return on secondary
        # Apply tilt to secondary (including 0 tilt)
        # Run real ray trace on configuration
    # Plot change in X on receiver as a function of motion in secondary for at least one of the tilts.

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
logging.basicConfig(filename='./log/secondary.log', format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w', level=logging.DEBUG)
logging.debug("Logging started.")

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"

#parameter = "x"
#values = np.arange(-10,11)/10.
#parameter = "alpha"
values = np.arange(-20,22,2)/10. #-2 to 2 degrees in 0.2 deg steps

# Apply tilt to secondary (including 0 tilt)
# Run real ray trace on configuration
#parameter = "alpha"
tilts = np.arange(-10,11,1)/10. #-1 to 1 degrees in 0.1 deg steps


for tilt in tilts:
    #def test_decenter(parameter, values):
    #    for value in values:
    # Set ref_wl for file descriptors.
    if ARRAY in ['1', '2']:
        ref_wl = 2070000
    elif ARRAY in ['3']:
        raise ValueError("Array 3 not yet supported.")
        #ref_wl = 3000000
    
    descriptors = ["secondary"]
    #if parameter in ['x', 'y', 'z']:
    #    descriptors = [parameter, "%smm"%(int(value*10))] # Note, this is done to avoid a decimal in the filename!
    #else:
    #    descriptors = [parameter, "%sdeg"%(str(value).replace('.','p'))]
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
    #arc_autov.decenter_cryostat(parameter, value)
    
    arc_autov.set_fields()
    arc_autov.set_vignetting()
    arc_autov.activate_pol_ray_trace()
    arc_autov.set_image_semi_aperture()
    
    surfaces = np.arange(6, 42).tolist()
    surfaces.reverse()
    
    for surface in surfaces:
        arc_autov.remove_surface(surface)
    
    arc_autov.enter_single_command("THI S6 0") # set thickness of image to zero
    arc_autov.enter_single_command("CIR S6 34") # set large circular aperture
    
    fields = np.arange(2, 26).tolist()
    fields.reverse()
    
    for field in fields:
        arc_autov.remove_field(field)
    
    arc_autov.set_vignetting()
    
    arc_autov.enter_single_command("DAR S4") # set decenter and return on secondary
    
    arc_autov.decenter_surface(4, "alpha", tilt)
    arc_autov.run_real_ray_trace(num_fields=1, alt_image=6, name_mod="%02d"%int(tilt*10))
    
    ## Setup to run tests in CODE V. These all need to be output to config files.
    #arc_autov.run_psf()
    #arc_autov.run_real_ray_trace()
    #arc_autov.run_poldsp(input_angle=0, pupil_number=23)
    ##arc_autov.run_poldsp(input_angle=90, pupil_number=23)
    
    arc_autov.exit()
    arc_autov.run()
#arc_autov.save_cfg()
#
#test_decenter("alpha", values)
#test_decenter("beta", values)
#test_decenter(parameter, [-2.0])

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
