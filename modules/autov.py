#!/usr/bin/python2
# Brian Koopman
"""Module for helping autov functions."""
import hashlib
import numpy as np

class AutoV(object):
    def __init__(self, array):
        self.array = array
        self.seq = []

    def create_header(self):
        # TODO: Add parameters to the header, which array, etc. anything in __init__.
        header = "! This .seq file was created by the AutoV automation class. \n"
        header += r"! How to run me: C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\autov\seq\script.seq"
        self.seq.append(header)
        return header

    def load_clean_len(self):
        # Check md5sum of "clean" files to make sure they're clean.
        md5sums = {'ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq': 'a90ffa3f0983dbb303ceec66ae689edd',
                   'ACTPol_90GHz_v29_optical_filter_aperture_study_20111204.seq': 'da8d3ecb420283261220ab4175b0a7d6'}

        clean_file_dir = "E:\ownCloud\optics\len\clean_copies\\"
        for item in md5sums.keys():
            md5 = hashlib.md5(open(clean_file_dir + item, 'rb').read()).hexdigest()
            if md5 != md5sums[item]:
                raise RuntimeError("The md5sum does not match a known value! This means a 'clean' file has been modified! Exiting.")
            else:
                print item, "md5sum matches, proceeding"

        if self.array in ['1', '2']:
            text = "! Load a clean copy of the optical design.\n"
            text += r'in "E:\ownCloud\optics\len\clean_copies\ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq"'
        else:
            raise ValueError("Automation only setup for array 1 and 2 at this time.")

        self.seq.append(text)
        return text

    def remove_glass(self):
        if self.array in ['1', '2']:
            text = "! automated glass defintion removal\n"
            surfaces = [6, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 34]
            for surface in surfaces:
                text += "GL1 S%s\n"%surface
            self.seq.append(text)
            return text
        else:
            raise ValueError("Automation only setup for array 1 and 2 at this time.")

    def apply_ar_coatings(self, coating_file=None):
        if self.array in ['1', '2']:
            text = "! apply MUL coating\n"
            if coating_file is None:
                coating_file = r"E:\ownCloud\optics\mul\two_layer_coating_138_250.mul"
            surfaces = [32, 33, 36, 37, 39, 40]
            for surface in surfaces:
                text += "MLT S%s %s\n"%(surface, coating_file)
            self.seq.append(text)
            return text
        else:
            raise ValueError("Automation only setup for array 1 and 2 at this time.")

    def set_wavelengths(self, wavelengths=None, reference=None):
        """Set the wavelengths in CODEV.

        Keyword arguments:
        wavelengths -- list of wavelengths, max length is 21
        reference -- change what the reference wavelength is
        """
        if wavelengths is None:
            wavelengths = []
        else:
            if len(wavelengths) > 21:
                raise ValueError("More than 21 wavelengths submitted, this is too many.")
            if len(wavelengths) != len(np.unique(wavelengths)):
                raise ValueError("Wavelengths submitted not unique, please remove duplicates.")

        text = "! modify wavelengths\n"
        text += "WTW W2 1\nWTW W3 1\n" # to modify defaults in clean copy

        for wavelength in wavelengths:
            text += "WL W%s %s\n"%(wavelengths.index(wavelength)+1, wavelength)

        text += "REF %s\n"%reference
        self.seq.append(text)
        return text

    def set_vignetting(self):
        text = "! set vignetting\n"
        text += "run " + r"C:\CODEV105_FCS\macro\setvig.seq" + " 1e-007 0.1 100 NO ;GO\n"
        self.seq.append(text)
        return text

    def activate_polarization_ray_tracing(self):
        """Active polarization ray tracing."""
        text = "! activate polarization ray tracing\n"
        text += "POL YES\n"
        self.seq.append(text)
        return text

    def set_fields(self):
        if self.array in ['2']:
            text = "! set polarization fraction of all fields to 1\n"
            for i in range(25):
                text += "PFR F%s 1\n"%(i+1)
            self.seq.append(text)
            return text
        else:
            ValueError("Automation not complete for arrays other than 2 right now.")

    def set_image_semi_aperture(self):
        if self.array in ['2']:
            text = "! Modify Semi-Aperture of Image surface for poldsp output\n"
            text += "CIR S42 8\n"
            self.seq.append(text)
            return text
        else:
            ValueError("Automation not complete for arrays other than 2 right now.")

    def quick_best_focus(self):       
        text = "! quick best focus, twice\n"
        text += "WAV ; BES; RFO; GO\n"
        text += "WAV ; BES; RFO; GO\n"
        self.seq.append(text)
        return text

    def run_psf(self): 
        text = "! auto_psf.seq\n"
        text += "OUT " + r"E:\owncloud\optics\data\tmp\psf.txt" + " ! Sets output file\n"
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
    # This is currently relying on the fact that wavelength is in nm and we want to give GHz.
    # wavelength given in nm
    return SPEED_OF_LIGHT/wavelength #[GHz]

def freq2lambda(freq):
    # freq in Ghz gives wavelength in nm, like CODEV wants
    return SPEED_OF_LIGHT/freq #[nm]

