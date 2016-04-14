import subprocess
import time
import os
import hashlib

DATE = time.strftime('%Y%m%d')
CTIME = int(time.time())

outDir = "E:\ownCloud\optics\data\\"
tmpDir = "E:\ownCloud\optics\data\\tmp\\"
autoseq = "pa2_automation.seq"

# Check md5sum of "clean" files to make sure they're clean.
md5sums = {'ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq': 'a90ffa3f0983dbb303ceec66ae689edd', 
           'ACTPol_90GHz_v29_optical_filter_aperture_study_20111204.seq': 'da8d3ecb420283261220ab4175b0a7d6'}

clean_file_dir = "E:\ownCloud\optics\len\clean_copies\\"
for item in md5sums.keys():
    md5 = hashlib.md5(open(clean_file_dir + item,'rb').read()).hexdigest()
    if md5 != md5sums[item]:
        raise RuntimeError("The md5sum does not match a known value! This means a 'clean' file has been modified! Exiting.")
        exit

# Make the CODEV Call
subprocess.call("C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\\autov\seq\%s"%(autoseq))

def checkDir(directory):
    if not os.path.exists(outDir + DATE):
        os.makedirs(outDir + DATE)

# Make copy of automation .seq file for permanent record
checkDir("%s%s"%(outDir,DATE))
print "cp E:\ownCloud\optics\\autov\seq\%s %s%s\\%s_%s"%(autoseq, outDir, DATE, CTIME, autoseq)
subprocess.call("cp E:\ownCloud\optics\\autov\seq\%s %s%s\\%s_%s"%(autoseq, outDir, DATE, CTIME, autoseq))

# Move temporary output files to permanent storage location
if (os.path.isfile("%s\psf.txt"%tmpDir)):
    checkDir("%s%s"%(outDir,DATE))
    print "mv %s\psf.txt %s%s\\%s_psf.txt"%(tmpDir,outDir,DATE,CTIME)
    subprocess.call("mv %s\psf.txt %s%s\\%s_psf.txt"%(tmpDir,outDir,DATE,CTIME))

if (os.path.isfile("%s\\real_ray_trace.txt"%tmpDir)):
    checkDir("%s%s"%(outDir,DATE))
    subprocess.call("mv %s\\real_ray_trace.txt %s%s\\%s_real_ray_trace.txt"%(tmpDir,outDir,DATE,CTIME))
