#!/usr/bin/python2
# Brian Koopman
"""Module for helping autov functions."""

class AutoV(object):
    def __init__(self, array):
        self.array = array
        self.seq = []

    def create_header(self):
        header = "! This .seq file was created by the AutoV automation class. \n"
        header += r"! How to run me: C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\autov\seq\script.seq"
        self.seq.append(header)
        return header

    def load_clean_len(self):
        if self.array in ['1', '2']:
            text = "! Load a clean copy of the optical design.\n"
            text += r'in "E:\ownCloud\optics\len\clean_copies\ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq"'
        else:
            raise ValueError("Automation only setup for array 1 and 2 at this time.")

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
