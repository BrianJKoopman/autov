import subprocess
import time
import os
import argparse
import autov

# Parse arguments passed to the script.
parser = argparse.ArgumentParser()
parser.add_argument("array", choices=['1','2','3'], help="Array you want to automate.")
args = parser.parse_args()

ARRAY = args.array
DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"
autoseq = "pa%s_automation.seq"%ARRAY

# Build .seq file for automated run.
qq = autov.AutoV(ARRAY)
qq.create_header()
qq.load_clean_len()
qq.remove_glass()
qq.apply_ar_coatings()
qq.set_wavelengths(wavelengths=[2140000, 2070000, 2000000], reference=2)
qq.set_vignetting()
qq.set_fields()
qq.activate_pol_ray_trace()
qq.set_image_semi_aperture()
qq.quick_best_focus()
#qq.run_psf()
qq.run_real_ray_trace()
qq.run_poldsp(input_angle=0, filename='poldsp_0deg.txt')
qq.run_poldsp(input_angle=90, filename='poldsp_90deg.txt')
qq.exit()

# Write the file
autov.writeseq(qq.seq, "E:\ownCloud\optics\\autov\seq\\autov.seq")

# Make the CODEV Call
#subprocess.call("C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\\autov\seq\%s"%(autoseq))
subprocess.call("C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\\autov\seq\\autov.seq")

def checkDir(directory):
    if not os.path.exists(outDir + DATE):
        os.makedirs(outDir + DATE)

# Move automation .seq file for permanent record
checkDir("%s%s"%(outDir,DATE))
print "mv E:\ownCloud\optics\\autov\seq\\autov.seq %s%s\\%s_autov.seq.pa%s"%(outDir, DATE, CTIME, ARRAY)
subprocess.call("mv E:\ownCloud\optics\\autov\seq\\autov.seq %s%s\\%s_autov.seq.pa%s"%(outDir, DATE, CTIME, ARRAY))

# Move temporary output files to permanent storage location
def store_output(filename, tmpDir, outDir, DATE, CTIME, ARRAY):
    if (os.path.isfile("%s\%s"%(tmpDir,filename))):
        checkDir("%s%s"%(outDir,DATE))
        print "mv %s\%s %s%s\\%s_%s.pa%s"%(tmpDir,filename,outDir,DATE,CTIME,filename,ARRAY)
        subprocess.call("mv %s\%s %s%s\\%s_%s.pa%s"%(tmpDir,filename,outDir,DATE,CTIME,filename,ARRAY))

store_output("psf.txt", tmpDir, outDir, DATE, CTIME, ARRAY)
store_output("real_ray_trace.txt", tmpDir, outDir, DATE, CTIME, ARRAY)
store_output("poldsp_0deg.txt", tmpDir, outDir, DATE, CTIME, ARRAY)
store_output("poldsp_90deg.txt", tmpDir, outDir, DATE, CTIME, ARRAY)
