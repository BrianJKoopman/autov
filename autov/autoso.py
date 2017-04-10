#!/usr/bin/python2
# Brian Koopman
# SO specific AutoV class.

from autov import AutoV, check_md5sums

class AutoSO(AutoV):
    """Class for writing custom .seq files for automating tolerancing of SO
    design in CODEV.

    The methods in this class will append the appropriate text for writing a
    .seq file which can be called by CODEV and used to automate tol
    parameters in a lens design.

    Attributes:
        seq (list[str]): List of strings which will be written sequentially to
                         a .seq file for running in CODEV
    """
    def __init__(self):
        super(AutoSO, self).__init__()

        self.out_dir = r"E:\ownCloud\simons_observatory\optics\data" + "\\"
        self.tmp_dir = r"E:\ownCloud\simons_observatory\optics\data\tmp" + "\\"

    def load_clean_len(self, seq_file):
        """Load a clean optical design.

        This method first checks the md5sums of both optical designs
        (regardless of the chosen one to load. These should never be modified,
        so it's good to check either way.

        The correct copy of the optical design is then setup to be imported to
        CODEV."""
        # Check md5sum of "clean" files to make sure they're clean.
        md5sums = {'Granet_CrDr_Prim5m_F3_20170219_9deg_f2920_Ls1270_folded_apertures.seq':
                   'b611e4429f45186451397ebeb540e3cd'}

        clean_file_dir = r"E:\ownCloud\simons_observatory\len" + "\\"

        check_md5sums(clean_file_dir, md5sums)

        text = "! Load a clean copy of the optical design.\n"
        #r'\Granet_CrDr_Prim6m_F3_20151007_folded_S7_f3000_Ls1860_start_3Dplot_v2.seq"' + \
        text += r'in "E:\ownCloud\simons_observatory\len' + \
                r'\%s"'%(seq_file) + \
                "\n"

        self.seq.append(text)
        return text

    # TODO: Move to autov, do not edit! Identical code in autoccatp.py
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
