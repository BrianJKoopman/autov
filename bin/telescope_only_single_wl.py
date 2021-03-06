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

# Build .seq file for automated run.
qq = autov.AutoV(ARRAY)
qq.create_header()
qq.load_clean_len()
qq.remove_glass()
qq.apply_ar_coatings()
if ARRAY in ['1', '2']:
    qq.set_wavelengths(wavelengths=[2140000, 2070000, 2000000], reference=1) # ar1, ar2
    ref_wl = 2070000
elif ARRAY in ['3']:
    qq.set_wavelengths(wavelengths=[3000000, 2070000, 1380000], reference=0) # ar3
    ref_wl = 3000000
qq.set_fields(polarization=0)
qq.set_vignetting()
qq.activate_pol_ray_trace()
qq.set_image_semi_aperture()

# just the telescope
qq.enter_single_command("DEL S6..41") # reduce to just the telescope
qq.enter_single_command("CIR S6 35") # increase semi-aperture of image
qq.quick_best_focus(force=True)

# Run tests
#qq.run_psf([str(int(ref_wl))])
#qq.run_real_ray_trace(file_descriptors=[str(int(ref_wl))])
qq.run_poldsp(input_angle=0, file_descriptors=[str(int(ref_wl))], pupil_number=23)

qq.exit()

# Write the file
autov.writeseq(qq.seq, "E:\ownCloud\optics\\autov\seq\\autov.seq")

# Make the CODEV Call
subprocess.call("C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\\autov\seq\\autov.seq")

# Move automation .seq file for permanent record
autov.check_dir("%s%s"%(outDir, DATE))
print "mv E:\ownCloud\optics\\autov\seq\\autov.seq %s%s\\%s_autov.seq.pa%s"%(outDir, DATE, CTIME, ARRAY)
subprocess.call("mv E:\ownCloud\optics\\autov\seq\\autov.seq %s%s\\%s_autov.seq.pa%s"%(outDir, DATE, CTIME, ARRAY))
