#!/usr/bin/python2
# Brian Koopman
# CCATp specific AutoV class.

import hashlib
from modules.autov import AutoV

class AutoCCATp(AutoV):
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
        for item in md5sums.keys():
            md5 = hashlib.md5(open(clean_file_dir + item, 'rb').read()).hexdigest()
            if md5 != md5sums[item]:
                raise RuntimeError("The md5sum does not match a known value! \
                      This means a 'clean' file has been modified! Exiting.")
            else:
                print item, "md5sum matches, proceeding"

        text = "! Load a clean copy of the optical design.\n"
        #r'\Granet_CrDr_Prim6m_F3_20151007_folded_S7_f3000_Ls1860_start_3Dplot_v2.seq"' + \
        text += r'in "E:\ownCloud\ccat\len' + \
                r'\%s"'%(seq_file) + \
                "\n"

        self.seq.append(text)
        return text
