#!/usr/bin/python2
# Brian Koopman
"""Module for helping autov functions."""
import hashlib

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
            text = "! apply MUL coating"
            if coating_file is None:
                coating_file = r"E:\ownCloud\optics\mul\two_layer_coating_138_250.mul" + "\n"
            surfaces = [32, 33, 36, 37, 39, 40]
            for surface in surfaces:
                text += "MLT S%s %s\n"%(surface, coating_file)
            self.seq.append(text)
            return text
        else:
            raise ValueError("Automation only setup for array 1 and 2 at this time.")

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
