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

wavelengths = []
# start, stop from 148.9 +/- 51/2.
for item in np.linspace(123.4, 174.4, num=21):
    wavelengths.append(autov.freq2lambda(item))

# Build .seq file for automated run.
qq = autov.AutoV(ARRAY)
qq.create_header()
qq.load_clean_len()
qq.remove_glass()
qq.apply_ar_coatings(coating_file=r"E:\ownCloud\optics\mul" + "\\" + "two_layer_coating_138_250_pa1_pa2_21_wavelengths.mul")
#qq.set_wavelengths(wavelengths=[2140000, 2070000, 2000000], reference=2)
qq.set_wavelengths(wavelengths=wavelengths, reference=10)
qq.set_fields(polarization=0)
qq.set_vignetting()
qq.activate_pol_ray_trace()
qq.set_image_semi_aperture()

for ref_wl in range(21):
    qq.set_wavelengths(wavelengths=wavelengths, reference=ref_wl)
    #qq.quick_best_focus()
    qq.run_psf([str(int(autov.lambda2freq(wavelengths[ref_wl])))])
    qq.run_real_ray_trace([str(int(autov.lambda2freq(wavelengths[ref_wl])))])
    qq.run_poldsp(input_angle=0, file_descriptors=[str(int(autov.lambda2freq(wavelengths[ref_wl])))], pupil_number=23)
    #qq.run_poldsp(input_angle=90, filename='poldsp_90deg.txt', pupil_number=23)
    #qq.run_poldsp(input_angle=0, filename='poldsp_0deg.txt')
    #qq.run_poldsp(input_angle=90, filename='poldsp_90deg.txt')

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
