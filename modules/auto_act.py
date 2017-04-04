#!/usr/bin/python2
# Brian Koopman
# ACTPol specific AutoV class.

import hashlib
import logging
from modules.autov import AutoV

class AutoACT(AutoV):
    def load_clean_len(self):
        """Load a clean optical design.

        General: N

        This method first checks the md5sums of both optical designs
        (regardless of the chosen one to load. These should never be modified,
        so it's good to check either way.

        The correct copy of the optical design is then setup to be imported to
        CODEV."""
        # Check md5sum of "clean" files to make sure they're clean.
        md5sums = {'ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq':
                   'a90ffa3f0983dbb303ceec66ae689edd',
                   'ACTPol_90GHz_v29_optical_filter_aperture_study_20111204.seq':
                   'da8d3ecb420283261220ab4175b0a7d6',
                   'AdvACT_HF_v31_20150416.seq':
                   '0027ace22465d607d8ffd6f53e62bed5'}

        clean_file_dir = r"E:\ownCloud\optics\len\clean_copies" + "\\"

        file_lookup = {'1': r'ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq',
                       '2': r'ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq',
                       '3': r'ACTPol_90GHz_v29_optical_filter_aperture_study_20111204.seq',
                       '4': r'AdvACT_HF_v31_20150416.seq'}

        for item in md5sums.keys():
            md5 = hashlib.md5(open(clean_file_dir + item, 'rb').read()).hexdigest()
            if md5 != md5sums[item]:
                logging.critical("md5sum mis-match: %s", item)
                logging.critical("Mis-match indicates a dirty starting file. Please examine.")
                raise RuntimeError("The md5sum does not match a known value! \
                      This means a 'clean' file has been modified! Exiting.")
            else:
                logging.info("md5sum match: %s", item)
                logging.info("Match indicates file unmodified, proceeding with script.")

        try:
            text = "! Load a clean copy of the optical design.\n"
            text += 'in "%s%s"\n'%(clean_file_dir, file_lookup[self.array])
            self.seq_file = "%s%s"%(clean_file_dir, file_lookup[self.array])
            logging.info("Loaded clean lens %s", file_lookup[self.array])
        except KeyError:
            logging.critical("Array %s not supported for loading a clean lens.", self.array)
            raise ValueError("Array %s not yet supported."%(self.array))

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
            text += "BDE S42 4.039980255467\n"

        self.seq.append(text)
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def remove_glass(self):
        """Remove glass definitions for polarization study.

        General: N

        We don't know the properties of the filters very well, so in my initial
        study I just removed all the glass definitions that weren't the silicon
        lenses. Do that again here.

        Note: The surfaces with a "glass" defined are the same in PA1 and PA2, but
        differ when referring to the files for PA3 and PA4.

        """
        text = "! automated glass defintion removal\n"
        if self.array in ['1', '2']:
            surfaces = [6, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 34]
            logging.info("Removed glass definitions from surfaces %s", surfaces)
        elif self.array in ['4']:
            surfaces = [6, 11, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 39]
            logging.info("Removed glass definitions from surfaces %s", surfaces)
        else:
            raise ValueError("Array %s not yet supported."%(self.array))
        for surface in surfaces:
            text += "GL1 S%s\n"%surface
        self.seq.append(text)
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def apply_ar_coatings(self, coating_file=None):
        """Apply .mul anti-reflection coatings to lenses.

        General: N

        Requires .mul file to already be generated from a .seq AR coating
        file.

        Note: AR coatings are optics tube dependant, be sure to load the
              appropriate one.
        """

        text = "! apply MUL coating\n"
        if self.array in ['1', '2']:
            surfaces = [32, 33, 36, 37, 39, 40]
        elif self.array in ['4']:
            surfaces = [37, 38, 41, 42, 44, 45]
        else:
            raise ValueError("Array %s not yet fully supported."%(self.array))

        if coating_file is None:
            if self.array in ['1', '2']:
                coating_file = r"E:\ownCloud\optics\mul\two_layer_coating_138_250.mul"
            elif self.array in ['3']:
                coating_file = r"E:\ownCloud\optics\mul\three_layer_coating_128_195_284.mul"
            elif self.array in ['4']:
                coating_file = r"E:\ownCloud\optics\mul\hf\three_layer_coating_120_185_285.mul"

        for surface in surfaces:
            text += "MLT S%s %s\n"%(surface, coating_file)
            logging.info("Applied .mul coating %s to S%s", coating_file, surface)
        self.seq.append(text)

        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def set_image_semi_aperture(self):
        """Enlarge the semi-aperture of the image surface for polarization
        studies.

        General: N
        """
        text = "! Modify Semi-Aperture of Image surface for poldsp output\n"

        if self.array in ['1', '2', '3']:
            image_surface = 42
        elif self.array in ['4']:
            image_surface = 47
        else:
            raise ValueError("Automation not complete for array %s right now."%(self.array))

        text += "CIR S%s 8\n"%(image_surface)
        logging.info("Semi-aperture of image surface increased for poldsp")
        self.seq.append(text)
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

