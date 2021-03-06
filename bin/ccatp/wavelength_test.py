import subprocess
import time
import os
import autotol
import numpy as np
import argparse

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("tolerance", choices=['DLX', 'DLY', 'DLZ', 'DLA', 'DLB', 'DLG'], help="Tolerance you want to automate.")
parser.add_argument("surface", choices=['3', '5', '8', '11'], help="Surface you want to tolerance.")
args = parser.parse_args()

tol = args.tolerance
sur = args.surface

if tol in ['DLX', 'DLY', 'DLZ']:
    units = 'cm'
    tol_range = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
elif tol in ['DLA', 'DLB', 'DLG']:
    units = 'rad'
    deg_range = (np.array(range(10))+1)/100.
    tol_range = (deg_range*np.pi/180.).tolist()

DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\ccat\optics\data\\"
tmpDir = "E:\ownCloud\ccat\optics\data\\tmp\\"

# Build .seq file for automated run.
qq = autotol.AutoTol()
qq.create_header()
qq.load_clean_len()
qq.set_buffer_len(20000)
qq.remove_receiver()
qq.enter_single_command('THC S11  100') #freeze the focal plane
qq.enter_single_command('THC S4  100') #freeze the other varying surface...

# Clear all wavelengths set in file.
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.set_wavelengths([2e5], 0)

# Clear the extra wavelengths set in the file.
qq.enter_single_command('DEL F0+1')
qq.enter_single_command('DEL F0+1')
qq.enter_single_command('DEL F0+1')
qq.enter_single_command('DEL F0+1')
qq.set_fields([(0.0, 0.0), (0.1875, 0.0), (0.0, 0.1875), (-0.1875, 0.0), (0.0, -0.1875), (0.375, 0.0), (0.0, 0.375), (-0.375, 0.0), (0.0, -0.375)])

qq.set_vignetting()

qq.quick_best_focus(force=True) #required for 200 um

qq.set_strehl_psf(["init"]) # this is needed to set the strehl option

for dis in tol_range:
    qq.set_tolerance(tol, sur, dis)
    qq.save_lens(r"E:\ownCloud\ccat\len\tmp\test.len")
    if units == 'cm':
        qq.run_tolfdif([tol, "S%s"%(sur), "%03d%s"%(dis, units)], r"E:\ownCloud\ccat\len\tmp\test.len")
    else:
        qq.run_tolfdif([tol, "S%s"%(sur), "%s%s"%(dis, units)], r"E:\ownCloud\ccat\len\tmp\test.len")
qq.exit()

# Write the file
autotol.writeseq(qq.seq, "E:\ownCloud\optics\\autotol\seq\\autotol.seq")

# Check for output date directory existence.
autotol.check_dir(qq.out_dir + qq.date)

# Make the CODEV Call
subprocess.call("C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\\autotol\seq\\autotol.seq")

# Move automation .seq file for permanent record
autotol.check_dir("%s%s"%(outDir, DATE))
print "mv E:\ownCloud\optics\\autotol\seq\\autotol.seq %s%s\\%s_autotol.seq"%(outDir, DATE, CTIME)
subprocess.call("mv E:\ownCloud\optics\\autotol\seq\\autotol.seq %s%s\\%s_autotol.seq"%(outDir, DATE, CTIME))
