#!/usr/bin/python2
# Brian Koopman
"""Module for helping autov functions."""
import hashlib
import subprocess
import os
import time
import numpy as np

from codey import get_fields

class AutoV(object):
    """Class for writing custom .seq files for automating CODEV.

    The methods in this class will append the appropriate text for writing a
    .seq file which can be called by CODEV and used to automate testing
    parameters in a lens design.

    Attributes:
        array (str): Which ACTPol array we're automating
        seq (list[str]): List of strings which will be written sequentially to
                         a .seq file for running in CODEV
    """
    def __init__(self, array):
        self.array = array
        self.seq = []

        self.out_dir = r"E:\ownCloud\optics\data" + "\\"
        self.tmp_dir = r"E:\ownCloud\optics\data\tmp" + "\\"

        self.date = time.strftime('%Y%m%d')
        self.ctime = int(time.time())

        self.wl_set = False # have wavelengths been set yet?
        self.wavelengths = None # save wavelengths after setting

    def create_header(self):
        """Create header comments for the .seq file."""
        # TODO: Add parameters to the header, which array, etc. anything in __init__.
        header = "! This .seq file was created by the AutoV automation class. \n"
        header += "! How to run me: " + \
                  r"C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\autov\seq\script.seq" + "\n"
        self.seq.append(header)
        return header

    def load_clean_len(self):
        """Load a clean optical design.

        This method first checks the md5sums of both optical designs
        (regardless of the chosen one to load. These should never be modified,
        so it's good to check either way.

        The correct copy of the optical design is then setup to be imported to
        CODEV."""
        # Check md5sum of "clean" files to make sure they're clean.
        md5sums = {'ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq':
                   'a90ffa3f0983dbb303ceec66ae689edd',
                   'ACTPol_90GHz_v29_optical_filter_aperture_study_20111204.seq':
                   'da8d3ecb420283261220ab4175b0a7d6'}

        clean_file_dir = r"E:\ownCloud\optics\len\clean_copies" + "\\"
        for item in md5sums.keys():
            md5 = hashlib.md5(open(clean_file_dir + item, 'rb').read()).hexdigest()
            if md5 != md5sums[item]:
                raise RuntimeError("The md5sum does not match a known value! \
                      This means a 'clean' file has been modified! Exiting.")
            else:
                print item, "md5sum matches, proceeding"

        if self.array in ['1', '2']:
            text = "! Load a clean copy of the optical design.\n"
            text += r'in "E:\ownCloud\optics\len\clean_copies' + \
                    r'\ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq"' + \
                    "\n"
        elif self.array in ['3']:
            text = "! Load a clean copy of the optical design.\n"
            text += r'in "E:\ownCloud\optics\len\clean_copies' + \
                    r'\ACTPol_90GHz_v29_optical_filter_aperture_study_20111204.seq"' + \
                    "\n"

        if self.array in ['1']:
            print "change to PA1 from PA2"
            text += "! PA1 needs to have optics mirrored from PA2 clean copy.\n"
            text += "XDE S8 -16.1\n"
            text += "XDE S15 -0.2\n"
            text += "XDE S24 -0.2\n"
            text += "XDE S25 -0.2\n"
            text += "XDE S29 -0.2\n"
            text += "XDE S30 -0.4338\n"
            text += "XDE S36 -0.9184880045643\n"
            text += "XDE S38 -0.9184880045643\n"
            text += "XDE S39 -1.38151498554729\n"
            text += "XDE S41 -1.38151498554729\n"
            text += "XDE S42 -1.6\n"

            text += "! can't forget your beta tilts!\n"
            text += "BDE S30 2.914\n"
            text += "BDE S43 4.039980255467\n"

        self.seq.append(text)
        return text

    def remove_glass(self):
        """Remove glass definitions for polarization study.

        We don't know the properties of the filters very well, so in my initial
        study I just removed all the glass definitions that weren't the silicon
        lenses. Do that again here.
        """
        text = "! automated glass defintion removal\n"
        surfaces = [6, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 34]
        for surface in surfaces:
            text += "GL1 S%s\n"%surface
        self.seq.append(text)
        return text

    def apply_ar_coatings(self, coating_file=None):
        """Apply .mul anti-reflection coatings to lenses.

        Requires .mul file to already be generated from a .seq AR coating
        file."""

        text = "! apply MUL coating\n"
        surfaces = [32, 33, 36, 37, 39, 40]

        if coating_file is None:
            if self.array in ['1', '2']:
                coating_file = r"E:\ownCloud\optics\mul\two_layer_coating_138_250.mul"
            elif self.array in ['3']:
                coating_file = r"E:\ownCloud\optics\mul\three_layer_coating_128_195_284.mul"

        for surface in surfaces:
            text += "MLT S%s %s\n"%(surface, coating_file)
        self.seq.append(text)

        return text

    def set_wavelengths(self, wavelengths, reference):
        """Set the wavelengths in CODEV.

        For studies that are wavelength dependant we need only a single WL to
        have weight 1, the rest 0. We set the reference wavelength to 1 and the
        rest to 0. So we always need both arguments.

        Warning:
        There are some pretty subtle difficulties with setting a bunch of
        wavelengths and then changing those wavelengths. Your best off setting
        all the wavelengths you want in the first call and not changing them,
        only passing the same set of wavelengths with a different reference
        number to change the REF and weight of the REF WL.

        Keyword arguments:
        wavelengths -- list of wavelengths, max length is 21
        reference -- change what the reference wavelength is (note, indexed on
                     0). The reference is used to change the weight of the
                     called wavelength to 1, the rest to 0.
        """
        if wavelengths is None:
            raise ValueError("No wavelenth specified, presumably just changing reference.")
        else:
            if len(wavelengths) > 21:
                raise ValueError("More than 21 wavelengths submitted, this is too many.")
            if len(wavelengths) != len(np.unique(wavelengths)):
                raise ValueError("Wavelengths submitted not unique, please remove duplicates.")

        if self.wl_set is True:
            if len(wavelengths) != len(self.wavelengths):
                raise ValueError("Please specify same number of wavelengths for each function call.")

        text = "! modify wavelengths\n"

        for wavelength in wavelengths:
            if wavelengths.index(wavelength) > 2: 
                # always skip first 3, which are set in both clean copies
                if self.wl_set == False:
                    text += "IN CV_MACRO:inswl %s+1\n"%(wavelengths.index(wavelength))
            if self.wl_set is False:
                text += "WL W%s %s\n"%(wavelengths.index(wavelength)+1, wavelength)
            if wavelengths.index(wavelength) is 0:
                text += "WTW W1 1\n" # always need a WL set to 1, make it the first
            if wavelengths.index(wavelength) is not 0:
                text += "WTW W%s 0\n"%(wavelengths.index(wavelength)+1) # set others to 0

        if reference is not None:
            text += "REF %s\n"%(reference+1)
            text += "WTW W%s 1\n"%(reference+1) # Change the weight of ref to 1

            if reference is not 0:
                text += "WTW W1 0\n" # set WL1 weight to 0 if it's not the ref

            self.seq.append(text)

        self.wl_set = True
        self.wavelengths = wavelengths

        return text

    def set_vignetting(self):
        """Run the default set vignetting command in CODEV."""
        text = "! set vignetting\n"
        text += "run " + r"C:\CODEV105_FCS\macro\setvig.seq" + " 1e-007 0.1 100 NO ;GO\n"
        self.seq.append(text)
        return text

    def activate_pol_ray_trace(self):
        """Active polarization ray tracing."""
        text = "! activate polarization ray tracing\n"
        text += "POL YES\n"
        self.seq.append(text)
        return text

    def set_fields(self):
        """Set the CODEV fields.

        Currently only defined for PA2, since they're already in the clean lens
        system file. This currently just sets the polarization fraction to 1
        for all fields, something we'll always want to do."""
        text = "! set fields\n"
        if self.array in ['1']:
            field_no = range(1, 26)
            fields = get_fields(int(self.array))

            text += "! set field x values\n"
            for (i, val) in zip(field_no, fields[:, 0].tolist()):
                text += "in CV_MACRO:cvsetfield X %s F%s\n"%(val, i)

            text += "! set field y values\n"
            for (i, val) in zip(field_no, fields[:, 1].tolist()):
                text += "in CV_MACRO:cvsetfield Y %s F%s\n"%(val, i)

            text += "! set polarization fraction of all fields to 1\n"
            for i in range(25):
                text += "PFR F%s 1\n"%(i+1)

        if self.array in ['2', '3']:
            text += "! set polarization fraction of all fields to 1\n"
            for i in range(25):
                text += "PFR F%s 1\n"%(i+1)

        text += "! set weights to 1 for all fields\n"
        for field in range(1, 26):
            text += "WTF F%s 1\n"%(field)

        self.seq.append(text)
        return text

    def set_image_semi_aperture(self):
        """Enlarge the semi-aperture of the image surface for polarization
        studies."""
        if self.array in ['1']:
            text = "! Modify Semi-Aperture of Image surface for poldsp output\n"
            text += "CIR S45 8\n"
            self.seq.append(text)
            return text
        if self.array in ['2', '3']:
            text = "! Modify Semi-Aperture of Image surface for poldsp output\n"
            text += "CIR S42 8\n"
            self.seq.append(text)
            return text
        else:
            ValueError("Automation not complete for array 1 right now.")

    def quick_best_focus(self):
        raise RuntimeError("Throwing this because you shouldn't be using quick_best focus.")
        #"""Insert two quick best focus commands."""
        #text = "! quick best focus, twice\n"
        #text += "WAV ; BES; RFO; GO\n"
        #text += "WAV ; BES; RFO; GO\n"
        #self.seq.append(text)
        #return text

    def run_psf(self, file_descriptors):
        """Run the point spread function commands.

        Will output psf results to a tmp file, psf.txt which will be moved by
        the user later for permanent storage."""
        # TODO: make a method for storing temporary files, rather than having
        # the user worry about it.
        # Can't have file name with any .'s other than in .txt
        filename = "psf"
        out_file = "%s%s\\%s_%s"%(self.out_dir, self.date, self.ctime, filename)
        for descriptor in file_descriptors:
            out_file += "_%s"%(descriptor)
        out_file += "_ar%s.txt"%(self.array)

        text = "! auto_psf.seq\n"
        text += "OUT " + out_file + " ! Sets output file\n"
        text += "! Script generated by PSF GUI interface.\n"
        text += "PSF; CAN;\n"
        text += "PSF\n"
        text += "TGR 1024\n"
        text += "PGR 1024\n"
        text += "NRD 51\n"
        text += "COM YES\n"
        text += "LIS NO\n"
        text += "PLO NO\n"
        text += "DIS NO\n"
        text += "GO\n"
        text += "OUT T ! Restores regular output\n"
        self.seq.append(text)
        return text

    def run_real_ray_trace(self, file_descriptors):
        """Run the real ray trace commands.

        Will output ray trace results to temp file, real_ray_trace.txt, which
        will be moved by the user later for permanent storage."""
        # TODO: This wants to know about the fields set.
        filename = "real_ray_trace"
        out_file = "%s%s\\%s_%s"%(self.out_dir, self.date, self.ctime, filename)
        for descriptor in file_descriptors:
            out_file += "_%s"%(descriptor)
        out_file += "_ar%s.txt"%(self.array)

        text = "! Adopted from auto_ray_trace.seq, which was used for 20141107 analysis\n"
        text += "OUT " + out_file + " ! Sets output file\n"
        for i in range(25):
            text += "RSI S42 R1 F%s\n"%(i+1)
        text += "OUT T ! Restores regular output\n"
        self.seq.append(text)
        return text

    def run_poldsp(self, input_angle, file_descriptors, pupil_number=11):
        """Run the poldsp macro for polarization studies.

        Keyword arguments:
        input_angle -- Sets the field orientation angle at the input for all
                       fields.
        filename -- Set the filename for temporary output. This is likely to
                    want to change based on input angle.
        pupil_number -- Number of rays across the pupil diameter."""
        # TODO: This also wants to know about the fields set
        filename = "poldsp"
        out_file = "%s%s\\%s_%s"%(self.out_dir, self.date, self.ctime, filename)
        out_file += "_%sdeg"%(input_angle)
        out_file += "_%srays"%(pupil_number)
        for descriptor in file_descriptors:
            out_file += "_%s"%(descriptor)
        out_file += "_ar%s.txt"%(self.array)

        text = "! Set input field orientation\n"
        for i in range(25):
            text += "POR F%s %s\n"%((i+1), input_angle)

        #text += "OUT " r"E:\owncloud\optics\data\tmp" + "\\" + filename + " ! Sets output file\n"
        text += "OUT " + out_file + " ! Sets output file\n"
        text += "RUN " r"C:\CODEV105_FCS\macro\poldsp.seq" + \
                " 0 %s \"Polarization State\" \"Full\"\n"%(pupil_number)
        text += "OUT T ! Restores regular output\n"
        self.seq.append(text)
        return text

    def enter_single_command(self, command):
        """Enter single command in event I don't have a method for it."""
        text = "! Manual command entry\n"
        text += "%s\n"%(command)
        self.seq.append(text)
        return text

    def exit(self):
        """Exit from CODEV without prompt."""
        text = "! exit without prompt when finished\n"
        text += "exit y\n"
        self.seq.append(text)
        return text

    #def store_output(filename, tmpDir, outDir, date, ctime, ARRAY):
    def store_output(self, filename, descriptors, date, ctime):
        check_dir("%s%s"%(self.out_dir, date))

        out_file = "%s%s\\%s_%s"%(self.out_dir, date, ctime, filename)
        for descriptor in descriptors:
            out_file += "_%s"%(descriptor)
        out_file += ".pa%s"%(self.array)

        # I guess we'll do this regardless of whether the file exists
        text = "! mv %s%s %s \n"%(self.tmp_dir, filename, out_file)
        self.seq.append(text) # inform the .seq script we're moving things

        if os.path.isfile("%s%s"%(self.tmp_dir, filename)):
            print "mv %s%s %s"%(self.tmp_dir, filename, out_file)
            subprocess.call("mv %s%s %s"%(self.tmp_dir, filename, out_file))

def byteify(input):
    # https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python/13105359#13105359
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def readseq(seqfile):
    """Read a CODEV sequence file, for use in combining a master .seq for
       automation."""
    with open(seqfile, 'r') as f:
        read_data = f.read()

    return read_data

def writeseq(inputs, seqfile):
    """Write the master CODEV sequence file.

    Keyword arguments:
    inputs -- list of input strings
    seqfile -- name of output .seq file"""
    with open(seqfile, 'w') as f:
        for item in inputs:
            f.write(item)
            f.write('\n')

SPEED_OF_LIGHT = 299792458 # [m/s]

def lambda2freq(wavelength):
    """Convert from wavelength to frequency.

    Keeping CODEV in mind, wavelengths in CODEV are in nm and we want GHz.

    Args:
        wavelength (float): wavelength in nm

    Returns:
        freq (float): Frequency in GHz
    """
    return SPEED_OF_LIGHT/float(wavelength) #[GHz]

def freq2lambda(freq):
    """Convert from frequency to wavelength.

    Keeping CODEV in mind, wavelengths in CODEV are in nm and we think in GHz.

    Args:
        freq (float): Frequency in GHz

    Returns:
        wavelength (float): wavelength in nm
    """
    return SPEED_OF_LIGHT/float(freq) #[nm]

#class AutoMul(object):
#    def __init__(self):
#    def
