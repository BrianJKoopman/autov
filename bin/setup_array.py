# To setup PA2 for use by hand.

import subprocess
import time
import os
import argparse
import autov
import numpy as np

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['1', '2', '3'], help="Array you want to automate.")
args = parser.parse_args()

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"
#autoseq = "pa%s_automation.seq"%ARRAY

# Build .seq file for automated run.
qq = autov.AutoV(ARRAY)
qq.create_header()
qq.load_clean_len()
qq.remove_glass()
qq.apply_ar_coatings()
if ARRAY in ['1', '2']:
    qq.set_wavelengths(wavelengths=[2140000, 2070000, 2000000], reference=1) # ar1, ar2
elif ARRAY in ['3']:
    qq.set_wavelengths(wavelengths=[3000000, 2070000, 1380000], reference=0) # ar3
qq.set_fields()
qq.set_vignetting()
qq.activate_pol_ray_trace()
qq.set_image_semi_aperture()
#qq.quick_best_focus()
#qq.run_psf()
#qq.run_real_ray_trace([str('%.2f'%(autov.lambda2freq(wavelengths[ref_wl])))])

# just the telescope
#qq.enter_single_command("DEL S6..41") # reduce to just the telescope
#qq.enter_single_command("CIR S6 35") # increase semi-aperture of image
#qq.quick_best_focus()
#qq.run_poldsp(input_angle=0, filename='poldsp_0deg_telescope_only_pa3_std_ref_wl_and_coating.txt', pupil_number=23)

#qq.exit()

# Write the file
autov.writeseq(qq.seq, "E:\ownCloud\optics\\autov\seq\\autov.seq")

# Make the CODEV Call
#subprocess.call("C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\\autov\seq\%s"%(autoseq))
subprocess.call("C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\\autov\seq\\autov.seq")

# Move automation .seq file for permanent record
autov.check_dir("%s%s"%(outDir, DATE))
print "mv E:\ownCloud\optics\\autov\seq\\autov.seq %s%s\\%s_autov.seq.pa%s"%(outDir, DATE, CTIME, ARRAY)
subprocess.call("mv E:\ownCloud\optics\\autov\seq\\autov.seq %s%s\\%s_autov.seq.pa%s"%(outDir, DATE, CTIME, ARRAY))
