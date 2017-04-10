# Tolerancing script for Granet_CrDr_Prim5m_F3_20170219_9deg_f2920_Ls1270_folded_apertures.seq
# Sumarizing tolerances on latest design for Optics Design Review

import subprocess
import time
import os
import numpy as np
import argparse

from autov import autov
from autov import autoso

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("tolerance", choices=['DLX', 'DLY', 'DLZ', 'DLT', 'DLA',
                                          'DLB', 'DLG'], help="Tolerance you want to automate.")
parser.add_argument("surface", choices=['3', '5', '8', '9'], help="Surface you want to tolerance.")
args = parser.parse_args()

tol = args.tolerance
sur = args.surface

wavelength = autov.freq2lambda(150) # GHz

seq_file = "Granet_CrDr_Prim5m_F3_20170219_9deg_f2920_Ls1270_folded_apertures.seq"

if tol in ['DLX', 'DLY', 'DLZ', 'DLT']:
    units = 'cm'
    #tol_range = (np.array(range(50))+1)/10. # 0 to 5 in 0.1 cm steps
    # 0 to 1 in 0.05 cm steps, 1 to 5 in 0.1 cm steps
    tol_range = np.hstack((np.arange(0.05, 1, 0.05), np.arange(1, 5, 0.1)))
    #tol_range = np.hstack((np.arange(0.05, 1, 0.10), np.arange(1, 5, 0.25), np.arange(5,10,0.5)))
    #tol_range = tol_range*10*1e3 #mm, then nm
    #units = 'nm' # changed to nm
    #tol_range = (np.array(range(10))+1)/1. # 0 to 5 in 0.1 cm steps
    #tol_range = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
elif tol in ['DLA', 'DLB', 'DLG']:
    # default angle units are radians in specing the tolerances
    units = 'rad'
    #deg_range = (np.array(range(200))+1)/100.
    deg_range = np.hstack((np.arange(0.010, 0.2, 0.005), np.arange(0.2, 2, 0.05))) # 0.01 0.2 in 0.005 deg steps to 0.2 to 2 degrees in 0.05 steps
    tol_range = (deg_range*np.pi/180.).tolist()

DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\simons_observatory\optics\data\\"
tmpDir = "E:\ownCloud\simons_observatory\optics\data\\tmp\\"

# Build .seq file for automated run.
qq = autoso.AutoSO(descriptors=["so_tol"])
qq.create_header()
qq.load_clean_len(seq_file)
qq.set_buffer_len(20000)

# set the wavelength
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.set_wavelengths([wavelength], 0) # 2mm

# Assign weight of 1 to fields that were set otherwise.
qq.enter_single_command('WTF F6 1')
qq.enter_single_command('WTF F10 1')

# Freeze varying surfaces.
qq.freeze_surface(4)
qq.freeze_surface(9)

# these are the fields, but they are already set.
#qq.set_fields([(0.0, 0.0), (2.25, 0.0), (-9.83506e-008, 2.25), (-2.25,
#-1.96701e-007), (2.6831e-008, -2.25), (4.5, 0.0), (3.18198, 3.18198),
#(-1.96701e-007, 4.5), (-3.18198, 3.18198), (-4.5, -3.93403e-007), (-3.18198,
#-3.18198),
#(5.3662e-008, -4.5), (3.18198, -3.18198)])

qq.set_vignetting()

qq.set_strehl_psf(["init"]) # this is needed to set the strehl option

for dis in tol_range:
    qq.set_tolerance(tol, sur, dis)
    qq.save_lens(r"E:\ownCloud\simons_observatory\len\tmp\test.len")
    if units in ['cm', 'nm']:
        dis_name = dis*10*1e3 #mm, then nm
        units = 'nm' # changed to nm
        qq.run_tolfdif([tol, "S%s"%(sur), "%s%s"%(str(int(dis_name)).zfill(5), units)], r"E:\ownCloud\simons_observatory\len\tmp\test.len")
    else:
        qq.run_tolfdif([tol, "S%s"%(sur), "%s%s"%(dis, units)], r"E:\ownCloud\simons_observatory\len\tmp\test.len")
qq.exit()
qq.run()
