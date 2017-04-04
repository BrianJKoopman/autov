import subprocess
import time
import os
import argparse
import autov
import numpy as np
import json

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("config", help="Pass in the config file.")
#parser.add_argument("array", choices=['1', '2', '3'], help="Array you want to automate.")
args = parser.parse_args()

# Parse new configuration file
f = open(args.config)
cfg = autov.byteify(json.loads(f.read()))

COATING_FILE = cfg['extract']['inputs']['coating_file']
FREQS = cfg['extract']['inputs']['freqs']
ARRAY = cfg['extract']['array']
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

# Output directories in windows.
outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"

# Setup wavelengths from input frequencies in cfg file
wavelengths = [autov.freq2lambda(item) for item in FREQS]
#wavelengths = [autov.freq2lambda(item) for item in [10., 20., 30., 40., 260., 270.0, 280.0, 290.0, 300.0, 310.0, 320.0, 330.0, 340.0, 350.0, 360.0, 370.0, 380.0, 390.0, 400.0, 410., 420.]]

# Build .seq file for automated run.
qq = autov.AutoV(ARRAY)
qq.create_header()
qq.load_clean_len()
qq.remove_glass()
qq.apply_ar_coatings(coating_file=r"E:\ownCloud\optics\mul" + "\\" + COATING_FILE)
#qq.set_wavelengths(wavelengths=[2140000, 2070000, 2000000], reference=2)
#qq.set_wavelengths(wavelengths=[3331000, 2070000, 1380000], reference=1)
qq.set_wavelengths(wavelengths=wavelengths, reference=10)
qq.set_fields()
qq.set_vignetting()
qq.activate_pol_ray_trace()
qq.set_image_semi_aperture()
#qq.run_psf([str(int(autov.lambda2freq(2070000)))])
#qq.run_real_ray_trace([str(int(autov.lambda2freq(2070000)))])
#qq.run_poldsp(input_angle=0, file_descriptors=[str(int(autov.lambda2freq(2070000)))], pupil_number=19)

for ref_wl in range(21):
    qq.set_wavelengths(wavelengths=wavelengths, reference=ref_wl)
    qq.run_psf([str(int(autov.lambda2freq(wavelengths[ref_wl])))])
    qq.run_real_ray_trace([str(int(autov.lambda2freq(wavelengths[ref_wl])))])
    qq.run_poldsp(input_angle=0, file_descriptors=[str(int(autov.lambda2freq(wavelengths[ref_wl])))], pupil_number=19)
    #qq.run_poldsp(input_angle=90, filename='poldsp_90deg.txt', pupil_number=23)
    #qq.run_poldsp(input_angle=0, filename='poldsp_0deg.txt')
    #qq.run_poldsp(input_angle=90, filename='poldsp_90deg.txt')
    #qq.store_output("psf.txt", [str(int(wavelengths[ref_wl]))], DATE, CTIME)
    #qq.store_output("real_ray_trace.txt", [str(int(wavelengths[ref_wl]))], DATE, CTIME)
    #qq.store_output("poldsp_0deg.txt", [str(int(wavelengths[ref_wl])), "23_rays"], DATE, CTIME)
    #qq.store_output("poldsp_90deg.txt", [str(int(wavelengths[ref_wl])), "23_rays"], DATE, CTIME)

qq.exit()

# Write the file
autov.writeseq(qq.seq, "E:\ownCloud\optics\\autov\seq\\autov.seq")

# Check for output date directory existence.
autov.check_dir(qq.out_dir + qq.date)

# Make the CODEV Call
subprocess.call("C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\\autov\seq\\autov.seq")

# Move automation .seq file for permanent record
autov.check_dir("%s%s"%(outDir, DATE))
print "mv E:\ownCloud\optics\\autov\seq\\autov.seq %s%s\\%s_autov.seq.pa%s"%(outDir, DATE, CTIME, ARRAY)
subprocess.call("mv E:\ownCloud\optics\\autov\seq\\autov.seq %s%s\\%s_autov.seq.pa%s"%(outDir, DATE, CTIME, ARRAY))
