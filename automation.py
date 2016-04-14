import subprocess
import time
import os
import hashlib
import argparse

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
print "cp E:\ownCloud\optics\\autov\seq\%s %s%s\\%s_pa%s_%s"%(autoseq, outDir, DATE, CTIME, ARRAY, autoseq)
subprocess.call("cp E:\ownCloud\optics\\autov\seq\%s %s%s\\%s_pa%s_%s"%(autoseq, outDir, DATE, CTIME, ARRAY, autoseq))

# Move temporary output files to permanent storage location
def store_output(filename, tmpDir, outDir, DATE, CTIME, ARRAY):
    if (os.path.isfile("%s\%s"%(tmpDir,filename))):
        checkDir("%s%s"%(outDir,DATE))
        print "mv %s\%s %s%s\\%s_pa%s_%s"%(tmpDir,filename,outDir,DATE,CTIME,ARRAY,filename)
        subprocess.call("mv %s\%s %s%s\\%s_pa%s_%s"%(tmpDir,filename,outDir,DATE,CTIME,ARRAY,filename))

store_output("psf.txt", tmpDir, outDir, DATE, CTIME, ARRAY)
store_output("real_ray_trace.txt", tmpDir, outDir, DATE, CTIME, ARRAY)
store_output("poldsp_0deg.txt", tmpDir, outDir, DATE, CTIME, ARRAY)
store_output("poldsp_90deg.txt", tmpDir, outDir, DATE, CTIME, ARRAY)

# cleanup
tmpDir = "E:\ownCloud\optics\data\\tmp\\"
subprocess.call("rm -i %s\*.txt"%(tmpDir))
