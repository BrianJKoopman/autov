#!/usr/bin/python2
# Brian Koopman
"""Module for helping autov functions."""

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
