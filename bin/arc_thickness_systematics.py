# Test polarization rotation result when thickness is changed +/- 2.5, 5%

import subprocess
import time
import argparse
import logging
from autov import autoact

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['1', '2', '3'], help="Array you want to automate.")
args = parser.parse_args()

# Setup logging
logging.basicConfig(filename='./log/arc_thickness.log', format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w', level=logging.DEBUG)
logging.debug("Logging started.")

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"

#coating_list = [(r"E:\ownCloud\optics\mul\ar_coating_sys\two_layer_coating_138_m0p05_250_m0p05.mul",["arc_n_change_m0p05"])]

coating_list = [([346750, 190000], r"E:\ownCloud\optics\mul\ar_coating_sys\arc_1380_346750_2500_190000.mul",["arc_1380_346750_2500_190000"]),
                ([355875, 195000], r"E:\ownCloud\optics\mul\ar_coating_sys\arc_1380_355875_2500_195000.mul",["arc_1380_355875_2500_195000"]),
                ([365000, 200000], r"E:\ownCloud\optics\mul\ar_coating_sys\arc_1380_365000_2500_200000.mul",["arc_1380_365000_2500_200000"]),
                ([374125, 205000], r"E:\ownCloud\optics\mul\ar_coating_sys\arc_1380_374125_2500_205000.mul",["arc_1380_374125_2500_205000"]),
                ([383250, 210000], r"E:\ownCloud\optics\mul\ar_coating_sys\arc_1380_383250_2500_210000.mul",["arc_1380_383250_2500_210000"])]

central_thicknesses = [365000, 200000]

def test_ar_coatings(coatings):
    for (thicknesses, coating, descriptors) in coatings:
        # Set ref_wl for file descriptors.
        if ARRAY in ['1', '2']:
            ref_wl = 2070000
        elif ARRAY in ['3']:
            raise ValueError("Array 3 not yet supported.")
            #ref_wl = 3000000

        # Build .seq file for automated run.
        arc_autov = autoact.AutoACT(ARRAY, descriptors)

        offset_value = (float(central_thicknesses[0] - thicknesses[0])/central_thicknesses[0])*100 #percent difference from original thickness
        index_variation_dict = {"type": "arc_thickness", "parameter": "index", "offset": offset_value, "units": "Percent"}
        arc_autov.add_to_json_cfg("perturbation", index_variation_dict)

        arc_autov.create_header()
        arc_autov.load_clean_len()
        arc_autov.remove_glass()
        arc_autov.apply_ar_coatings(coating_file = coating)
        if ARRAY in ['1', '2']:
            arc_autov.set_wavelengths(wavelengths=[2140000, 2070000, 2000000], reference=1) # ar1, ar2
        elif ARRAY in ['3']:
            #arc_autov.set_wavelengths(wavelengths=[3000000, 2070000, 1380000], reference=0) # ar3
            raise ValueError("Array 3 not yet supported.")
        arc_autov.set_fields()
        arc_autov.set_vignetting()
        arc_autov.activate_pol_ray_trace()
        arc_autov.set_image_semi_aperture()
        arc_autov.run_psf()
        arc_autov.run_real_ray_trace()
        arc_autov.run_poldsp(input_angle=0, pupil_number=23)
        #arc_autov.run_poldsp(input_angle=90, pupil_number=23)
        arc_autov.exit()
        arc_autov.run()
        arc_autov.save_cfg(out_dir="./output/arc_thickness/")

test_ar_coatings(coating_list)

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
