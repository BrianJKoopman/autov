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
        super(AutoCCATp, self).__init__()

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

    def set_strehl_psf(self, file_descriptors):
        """Run the point spread function commands.

        Will output psf results to a tmp file, psf.txt which will be moved by
        the user later for permanent storage."""
        # TODO: make a method for storing temporary files, rather than having
        # TODO: I might only really need the INT STR command, should test this.
        # the user worry about it.
        # Can't have file name with any .'s other than in .txt
        filename = "psf"
        out_file = "%s%s\\%s_%s"%(self.out_dir, self.date, self.ctime, filename)
        for descriptor in file_descriptors:
            out_file += "_%s"%(descriptor)
        out_file += ".txt"

        text = "! psf with strehl option set\n"
        text += "OUT " + out_file + " ! Sets output file\n"
        text += "! Script generated by PSF GUI interface.\n"
        text += "PSF\n"
        text += "INT STR\n"
        text += "PLO NO\n"
        text += "GO\n"
        text += "OUT T ! Restores regular output\n"
        self.seq.append(text)
        return text

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

    def run_tolfdif(self, file_descriptors, lens_file):
        """Run the finite difference analysis for tolerancing."""
        # TODO: make a method for storing temporary files, rather than having
        # the user worry about it.
        # Can't have file name with any .'s other than in .txt
        filename = "tolfdif"
        out_file = "%s%s\\%s_%s"%(self.out_dir, self.date, self.ctime, filename)
        for descriptor in file_descriptors:
            out_file += "_%s"%(descriptor)
        out_file += ".txt"

        text = "! tolfdif automation\n"
        text += "OUT " + out_file + " ! Sets output file\n"
        text += "! Script generated by TOLFDIF GUI interface.\n"
        text += "!TOLFDIF\n"
        text += "in cv_macro:tolfdif \"%s\" cv_macro:tolstrehl CV_MACRO:tolcomp YNNN\n"%(lens_file)
        text += "GO\n"
        text += "OUT T ! Restores regular output\n"
        self.seq.append(text)
        return text

    def set_tolerance(self, tolerance, surface, value):
        """Set tolerance for a surface."""
        tolerances = ["DLX", "DLY", "DLZ", "DLT", "DLA", "DLB", "DLG"]
        if tolerance in tolerances:
            text = "! Set tolerance %s for surface %s to %s\n"%(tolerance, surface, value)
            text += "%s S%s V %s\n"%(tolerance, surface, value)
            self.seq.append(text)
        else:
            raise ValueError("Unknown tolerance.")
        return text

    def save_lens(self, filename):
        """Save the lens file to temporary location for running tolfdif."""
        text = "! Save lens file\n"
        text += "SAV \"%s\"\n"%(filename)
        self.seq.append(text)
        return text

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
