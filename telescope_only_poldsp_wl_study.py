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

wavelengths = [autov.freq2lambda(item) for item in np.linspace(50, 250, num=21)]

# Old wavelengths
# start, stop from 148.9 +/- 51/2.
#for item in np.linspace(123.4, 174.4, num=21):
#    wavelengths.append(autov.freq2lambda(item))

# Build .seq file for automated run.
qq = autov.AutoV(ARRAY)
qq.create_header()
qq.load_clean_len()
qq.remove_glass()
qq.apply_ar_coatings(coating_file=r"E:\ownCloud\optics\mul" + "\\" + "three_layer_coating_128_195_284_21_wavelengths_50_250.mul")
qq.set_wavelengths(wavelengths=wavelengths, reference=10)
qq.set_fields()
qq.set_vignetting()
qq.activate_pol_ray_trace()
qq.set_image_semi_aperture()

# just the telescope
qq.enter_single_command("DEL S6..41") # reduce to just the telescope
qq.enter_single_command("CIR S6 35") # increase semi-aperture of image
qq.quick_best_focus()

for ref_wl in range(21):
    qq.set_wavelengths(wavelengths=wavelengths, reference=ref_wl)
    qq.quick_best_focus()
    #qq.run_psf([str(int(autov.lambda2freq(wavelengths[ref_wl])))])
    #qq.run_real_ray_trace([str(int(autov.lambda2freq(wavelengths[ref_wl])))])
    qq.run_poldsp(input_angle=0, file_descriptors=[str(int(autov.lambda2freq(wavelengths[ref_wl]))), 'telescope_only'], pupil_number=15)

qq.exit()

# Write the file
autov.writeseq(qq.seq, "E:\ownCloud\optics\\autov\seq\\autov.seq")

# Make the CODEV Call
subprocess.call("C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\\autov\seq\\autov.seq")

# Move automation .seq file for permanent record
autov.check_dir("%s%s"%(outDir, DATE))
print "mv E:\ownCloud\optics\\autov\seq\\autov.seq %s%s\\%s_autov.seq.pa%s"%(outDir, DATE, CTIME, ARRAY)
subprocess.call("mv E:\ownCloud\optics\\autov\seq\\autov.seq %s%s\\%s_autov.seq.pa%s"%(outDir, DATE, CTIME, ARRAY))
