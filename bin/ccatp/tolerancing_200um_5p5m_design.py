import subprocess
import time
import os
import autotol
import numpy as np
import argparse

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("tolerance", choices=['DLX', 'DLY', 'DLZ', 'DLT', 'DLA',
                                          'DLB', 'DLG'], help="Tolerance you want to automate.")
parser.add_argument("surface", choices=['3', '5', '7', '8', '11'], help="Surface you want to tolerance.")
parser.add_argument("-t","--tertiary", help="Add tertiary mirror.", action="store_true")
args = parser.parse_args()

tol = args.tolerance
sur = args.surface

wavelength = 2e6 #2mm
#wavelength = 2e5 #200um

# seq_file needs to be in /home/koopman/ownCloud/niemack_lab/ccat/len/
# there are likely unique steps in the automated .seq file based on which file
# we're loading, so right now this is broken up into different scripts.
seq_file = "Granet_CrDr_Prim5p5m_F3_20160820_S7_f3210_Ls1345.seq"
#seq_file = "ccatp_design_bjk_20160812.seq"

if tol in ['DLX', 'DLY', 'DLZ', 'DLT']:
    units = 'cm'
    #tol_range = (np.array(range(50))+1)/10. # 0 to 5 in 0.1 cm steps
    # 0 to 1 in 0.05 cm steps, 1 to 5 in 0.1 cm steps
    #tol_range = np.hstack((np.arange(0.05, 1, 0.05), np.arange(1, 5, 0.1)))
    tol_range = np.hstack((np.arange(0.05, 1, 0.10), np.arange(1, 5, 0.25), np.arange(5,10,0.5)))
    #tol_range = tol_range*10*1e3 #mm, then nm
    #units = 'nm' # changed to nm
    #tol_range = (np.array(range(10))+1)/1. # 0 to 5 in 0.1 cm steps
    #tol_range = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
elif tol in ['DLA', 'DLB', 'DLG']:
    units = 'rad'
    #deg_range = (np.array(range(200))+1)/100.
    deg_range = np.hstack((np.arange(0.010, 0.2, 0.005), np.arange(0.2, 2, 0.05))) # 0.01 0.2 in 0.005 deg steps to 0.2 to 2 degrees in 0.05 steps
    tol_range = (deg_range*np.pi/180.).tolist()

DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\ccat\optics\data\\"
tmpDir = "E:\ownCloud\ccat\optics\data\\tmp\\"

# Build .seq file for automated run.
qq = autotol.AutoTol()
qq.create_header()
qq.load_clean_len(seq_file)
qq.set_buffer_len(20000)
#qq.remove_receiver()
qq.enter_single_command('THC S7  100') #freeze the focal plane
qq.enter_single_command('THC S4  100') #freeze the other varying surface...
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')
qq.enter_single_command('DEL W0+1')

# set the wavelength
qq.set_wavelengths([wavelength], 0) # 2mm

# Clear the extra fields set in the file.
qq.enter_single_command('DEL F0+1')
qq.enter_single_command('DEL F0+1')
qq.enter_single_command('DEL F0+1')
qq.enter_single_command('DEL F0+1')

# 200 um and 2mm  field set
if wavelength == 2e5:
    qq.set_fields([(0.0, 0.0), (0.1875, 0.0), (0.0, 0.1875), (-0.1875, 0.0), (0.0, -0.1875), (0.375, 0.0), (0.0, 0.375), (-0.375, 0.0), (0.0, -0.375)])
elif wavelength == 2e6:
    qq.set_fields([(0.0, 0.0), (1.825, 0.0), (0.0, 1.825), (-1.825, 0.0), (0.0, -1.825), (3.65, 0.0), (0.0, 3.65), (-3.65, 0.0), (0.0, -3.65)])

qq.enter_single_command('YDE S7 0') # remove Y-decenter on focal plane

# add tertiary
if args.tertiary:
    qq.enter_single_command('INS S7..9') # add three surfaces for tertiary placement
    if sur == '7': # if 7, we're interested in the focal plane, else it's probably 8 and we're looking at the tertiary
        print "adding 3 surfaces"
        sur = str(int(sur) + 3) # add 3 surfaces to the surface number for the focal plane
        print sur
    qq.enter_single_command("SLB S8 'tertiary'") #name surface
    qq.enter_single_command("THI  S7 -380") # place before the focus 3800 mm
    qq.enter_single_command("RMD  S8 REFL") # make the mirror reflective
    qq.enter_single_command("XDE S8 (XDE S8)") # set basic decenter
    qq.enter_single_command("ADE  S8 -45") # set 45 degree angle
    qq.enter_single_command("XDE S9 (XDE S9)") # set basic decenter
    qq.enter_single_command("ADE  S9 -45") # set 45 degree angle
    qq.quick_best_focus(force=True) # run a quick best focus to put the focal plane in the right spot

qq.set_vignetting()

qq.quick_best_focus(force=True) #required for 200 um

qq.set_strehl_psf(["init"]) # this is needed to set the strehl option

for dis in tol_range:
    qq.set_tolerance(tol, sur, dis)
    qq.save_lens(r"E:\ownCloud\ccat\len\tmp\test.len")
    if units in ['cm', 'nm']:
        dis_name = dis*10*1e3 #mm, then nm
        units = 'nm' # changed to nm
        qq.run_tolfdif([tol, "S%s"%(sur), "%s%s"%(str(int(dis_name)).zfill(5), units)], r"E:\ownCloud\ccat\len\tmp\test.len")
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
