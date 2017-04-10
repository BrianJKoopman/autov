#!/usr/bin/python2
# Brian Koopman
# CCATp specific AutoV class.

from autov import AutoV, check_md5sums

class AutoCCATp(AutoV):
    """Class for writing custom .seq files for automating tolerancing of CCATp
    design in CODEV.

    The methods in this class will append the appropriate text for writing a
    .seq file which can be called by CODEV and used to automate tol
    parameters in a lens design.

    Attributes:
        seq (list[str]): List of strings which will be written sequentially to
                         a .seq file for running in CODEV
    """
    def __init__(self):
        super(AutoCCATp, self).__init__()

        self.out_dir = r"E:\ownCloud\ccat\optics\data" + "\\"
        self.tmp_dir = r"E:\ownCloud\ccat\optics\data\tmp" + "\\"
    def load_clean_len(self, seq_file):
        """Load a clean optical design.

        This method first checks the md5sums of both optical designs
        (regardless of the chosen one to load. These should never be modified,
        so it's good to check either way.

        The correct copy of the optical design is then setup to be imported to
        CODEV."""
        # Check md5sum of "clean" files to make sure they're clean.
        md5sums = {'Granet_CrDr_Prim6m_F3_20151007_folded_S7_f3000_Ls1860_start_3Dplot_v2.seq':
                   'af2165b5a3a53925441738e3b9be0090',
                   'ccatp_design_bjk_20160812.seq':
                   'ef1457d87b844402a201dde666061c95',
                   'Granet_CrDr_Prim5p5m_F3_20160820_S7_f3210_Ls1345.seq':
                   'b10e35a3a0c1dd753dd5a0866462b489'}

        clean_file_dir = r"E:\ownCloud\ccat\len" + "\\"

        check_md5sums(clean_file_dir, md5sums)

        text = "! Load a clean copy of the optical design.\n"
        #r'\Granet_CrDr_Prim6m_F3_20151007_folded_S7_f3000_Ls1860_start_3Dplot_v2.seq"' + \
        text += r'in "E:\ownCloud\ccat\len' + \
                r'\%s"'%(seq_file) + \
                "\n"

        self.seq.append(text)
        return text

    #TODO: use super call to instead call autov.remove_surface()
    def remove_receiver(self):
        """Remove receiver definition for tolerancing study.

        For his paper Mike made a receiver looking surface that we don't want
        for the tolerancing analysis.
        """
        text = "! automated glass defintion removal\n"
        surfaces = [11]
        for surface in surfaces:
            text += "DEL S%s\n"%surface
        self.seq.append(text)
        return text

    # TODO: Move to autov, do not edit! Identical code in autoso.py
    def set_fields(self, fields):
        """Set the CODEV fields.

        Currently only defined for PA2, since they're already in the clean lens
        system file. This currently just sets the polarization fraction to 1
        for all fields, something we'll always want to do."""
        text = "! set fields\n"
        for i in range(len(fields)):
            text += "in CV_MACRO:cvsetfield X %s F%s\n"%(fields[i][0], i+1)
            text += "in CV_MACRO:cvsetfield Y %s F%s\n"%(fields[i][1], i+1)
            text += "WTF F%s 1\n"%(i+1)
        self.seq.append(text)
        return text

def writeseq(inputs, seqfile):
    """Write the master CODEV sequence file.

    Keyword arguments:
    inputs -- list of input strings
    seqfile -- name of output .seq file"""
    with open(seqfile, 'w') as f:
        for item in inputs:
            f.write(item)
            f.write('\n')
