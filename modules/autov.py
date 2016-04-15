#!/usr/bin/python2
# Brian Koopman
"""Module for helping autov functions."""

class AutoV(object):
    def __init__(self, array):
        self.array = array
        self.seq = []
    def create_header(self):
        header = "! This .seq file was created by the autov automation class. \n"
        header += r"! How to run me: C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\seq\script.seq"
        self.seq.append(header)

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
