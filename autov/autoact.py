#!/usr/bin/python2
# Brian Koopman
# ACTPol specific AutoV class.

import logging
import numpy as np

from autov import AutoV, check_md5sums
from parse_seq import read_seq, parse_surface

class AutoACT(AutoV):
    def __init__(self, array, descriptors):
        super(AutoACT, self).__init__(array, descriptors)

        #: A string describes the ACTPol array number.
        self.array = array

        #: A list of strings which will be written sequentially to the name of output files.
        self.descriptors = descriptors

        self.seq_file = None

        self.out_dir = r"E:\ownCloud\optics\data" + "\\"
        self.tmp_dir = r"E:\ownCloud\optics\data\tmp" + "\\"

        #: Dictionary containing information to be written to a codevpol style cfg file.
        self.cfg_dict = {"array": int(self.array),
                         "codev_inputs": {}
                        }

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
                       '4': r'ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq',
                       '5': r'ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq',
                       '6': r'ACTPol_90GHz_v29_optical_filter_aperture_study_20111204.seq'}

        check_md5sums(clean_file_dir, md5sums)

        try:
            text = "! Load a clean copy of the optical design.\n"
            text += 'in "%s%s"\n'%(clean_file_dir, file_lookup[self.array])
            self.seq_file = "%s%s"%(clean_file_dir, file_lookup[self.array])
            logging.info("Loaded clean lens %s", file_lookup[self.array])
        except KeyError:
            logging.critical("Array %s not supported for loading a clean lens.", self.array)
            raise ValueError("Array %s not yet supported."%(self.array))

        if self.array in ['1', '4']:
            print "change to PA1/4 from PA2"
            text += "! PA1/4 needs to have optics mirrored from PA2 clean copy.\n"
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
        if self.array in ['1', '2', '3', '4', '5', '6']:
            surfaces = [6, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 34]
            logging.info("Removed glass definitions from surfaces %s", surfaces)
        #elif self.array in ['4']:
        #    surfaces = [6, 11, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 39]
        #    logging.info("Removed glass definitions from surfaces %s", surfaces)
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
        if self.array in ['1', '2', '3', '4', '5', '6']:
            surfaces = [32, 33, 36, 37, 39, 40]
        #elif self.array in ['4']:
        #    surfaces = [37, 38, 41, 42, 44, 45]
        else:
            raise ValueError("Array %s not yet fully supported."%(self.array))

        if coating_file is None:
            if self.array in ['1', '2']:
                coating_file = r"E:\ownCloud\optics\mul\two_layer_coating_138_250.mul"
            elif self.array in ['3', '6']:
                coating_file = r"E:\ownCloud\optics\mul\three_layer_coating_128_195_284.mul"
            elif self.array in ['4']:
                #coating_file = r"E:\ownCloud\optics\mul\hf\three_layer_coating_120_185_285.mul"
                coating_file = r"E:\ownCloud\optics\mul\hf\three_layer_coating_152_183_296.mul"
            elif self.array in ['5']:
                coating_file = r"E:\ownCloud\optics\mul\mf\three_layer_coating_257_310_500.mul"

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

        if self.array in ['1', '2', '3', '4', '5', '6']:
            image_surface = 42
        #elif self.array in ['4']:
        #    image_surface = 47
        else:
            raise ValueError("Automation not complete for array %s right now."%(self.array))

        text += "CIR S%s 8\n"%(image_surface)
        logging.info("Semi-aperture of image surface increased for poldsp")
        self.seq.append(text)
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def decenter_cryostat(self, parameter, offset):
        """Apply a "Basic" decenter to window, decentering entire cryostat.

        General: N

        Units: ADE and BDE are in degrees, XDE, YDE, ZDE are in System Units.

        :param parameter: Parameter to decenter. This corresponds to any
                          decenter parameter in CODE V. We're focusing on x, y,
                          z, alpha and beta.
        :type parameter: str
        :param offset: Offset value, from current, for decenter in system units.
        :type offset: float

        """
        #TODO: Ugh, this needs to be broken up a bit I think, so that it's
        #      decenter a general surface.
        parameter_lookup = {"x": "XDE", "y": "YDE", "z": "ZDE", "alpha": "ADE", "beta": "BDE"}
        decenter_command = parameter_lookup[parameter.lower()]

        if self.array in ['1', '2']:
            text = "! Apply Decenter to window clamp, decentering entire cryostat/optics tube.\n"
            window_clamp_surface = 8

            # Determine current value for decenter
            # TODO: For PA1, we set decenters. Should use parse the
            # surfaces before setting those and record these values as we set
            # them.
            seq_dict = parse_surface(read_seq(self.seq_file), window_clamp_surface)
            #print seq_dict
            #print "Current %s value: %s"%(decenter_command, seq_dict[decenter_command])
            logging.debug("Original %s value: %s", decenter_command, seq_dict[decenter_command])
            new_decenter = seq_dict[decenter_command] + offset
            logging.debug("New %s value set to: %s", decenter_command, new_decenter)

            text += "%s S%s %s\n"%(decenter_command, str(window_clamp_surface), str(new_decenter))
            self.seq.append(text)
            logging.debug("Adding text to .seq file: \n%s", text)
            return text
        else:
            ValueError("Automation not complete for array 1 right now.")

    def run_real_ray_trace(self, num_fields=None, alt_image=0, name_mod=None):
        """Run the real ray trace commands.

        General: N
        TODO: Pass image surface in as option.

        Will output ray trace results to temp file, real_ray_trace.txt, which
        will be moved by the user later for permanent storage.

        :param alt_image: If the image isn't a default image, provide the int for it here.
        """
        # TODO: This wants to know about the fields set.
        if name_mod is None:
            filename = "real_ray_trace"
        else:
            filename = "real_ray_trace_%s"%(name_mod)
        out_file = self._make_windows_md5_out_file(filename)
        # Add ray trace file output to cfg_dict.
        dict_out_file = self._make_cfg_dict_out_file_from_full_path(out_file)
        self.cfg_dict["codev_inputs"]["ray_trace"] = [dict_out_file]

        # Definte image_surface defaults or take alt_image
        if alt_image is 0:
            if self.array in ['1', '2', '3', '4', '5', '6']:
                image_surface = 42
            #elif self.array in ['4']:
            #    image_surface = 47
            else:
                raise ValueError("Automation not complete for array %s right now."%(self.array))
        else:
            image_surface = alt_image

        text = "! Adopted from auto_ray_trace.seq, which was used for 20141107 analysis\n"
        text += "OUT " + out_file + " ! Sets output file\n"

        # Set number of fields to 25 as default.
        if num_fields is None:
            num_fields = 25

        for i in range(num_fields):
            text += "RSI S%s R1 F%s\n"%(image_surface, i+1)
        text += "OUT T ! Restores regular output\n"
        self.seq.append(text)
        logging.info("RSI .seq inserted")

        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def set_fields(self, array_loc=None, polarization=1):
        """Set the CODEV fields.

        General: N
        TODO: Fields fetched from get_fields, which could be okay, but also it's array specific.
        TODO: Pass fields list in, delete all fields (if possible) and enter in new fields.

        Currently only defined for PA2, since they're already in the clean lens
        system file. This currently just sets the polarization fraction to 1
        for all fields, something we'll always want to do."""
        text = "! set fields\n"

        # This way we can choose an array position (PA1 for looking at HF for instance).
        if array_loc is None:
            _array = self.array
        else:
            _array = array_loc

        if _array in ['1', '4']:
            field_no = range(1, 26)
            fields = get_fields(int(_array))

            text += "! set field x values\n"
            for (i, val) in zip(field_no, fields[:, 0].tolist()):
                text += "in CV_MACRO:cvsetfield X %s F%s\n"%(val, i)

            text += "! set field y values\n"
            for (i, val) in zip(field_no, fields[:, 1].tolist()):
                text += "in CV_MACRO:cvsetfield Y %s F%s\n"%(val, i)

            text += "! set polarization fraction of all fields to 1\n"
            for i in range(25):
                text += "PFR F%s %s\n"%(i+1, polarization)

        # Note the change above to identify position won't work for MF1/2 and
        # PA2 and PA3, since those fields will probably differ.
        if _array in ['2', '3', '5', '6']:
            text += "! set polarization fraction of all fields to 1\n"
            for i in range(25):
                text += "PFR F%s %s\n"%(i+1, polarization)

        text += "! set weights to 1 for all fields\n"
        for field in range(1, 26):
            text += "WTF F%s 1\n"%(field)

        logging.info("Fields set.")
        self.seq.append(text)
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def perturb_lens_thickness(self, lens, amount):
        if lens == 1:
            super(AutoACT, self).delete_solve(32)
            super(AutoACT, self).freeze_surface(32)
            #TODO: Need to extract Surface thickness from S command in .seq file with parse_seq module. Needs to be written to do this.

# Pulled from codevpol to avoid moby2 dependancy in autov...
def get_fields(array):
    """Retrieve the fields input to CODEV, these are sky coordinates.

    :param array: Which optics tube you want fields for, PA1 or PA2.
    :type array: int
    """
    ## PA1 - Zoom 3
    #pa1_fields = np.around(np.array([[0.625000,0.480000],
    #[0.456667,0.480000],
    #[0.625000,0.648333],
    #[0.793333,0.480000],
    #[0.625000,0.311667],
    #[0.288333,0.480000],
    #[0.386941,0.718059],
    #[0.625000,0.816667],
    #[0.863059,0.718059],
    #[0.961667,0.480000],
    #[0.863059,0.241941],
    #[0.625000,0.143333],
    #[0.386941,0.241941],
    #[0.120000,0.480000],
    #[0.187657,0.732500],
    #[0.372500,0.917343],
    #[0.625000,0.985000],
    #[0.877500,0.917343],
    #[1.06234,0.732500],
    #[1.13000,0.480000],
    #[1.06234,0.227500],
    #[0.877500,0.0426571],
    #[0.625000,-0.0250000],
    #[0.372500,0.0426571],
    #[0.187657,0.227500]]),4)

    # Added on 2014-12-08 when I realized my python script exports the fields
    # in a different order for PA1 and PA2.
    pa1_fields = np.around(np.array([[0.625, 0.48], [0.7933, 0.48],
                                     [0.625, 0.6483], [0.4567, 0.48],
                                     [0.625, 0.3117], [0.9617, 0.48],
                                     [0.8631, 0.7181], [0.625, 0.8167],
                                     [0.3869, 0.7181], [0.2883, 0.48],
                                     [0.3869, 0.2419], [0.625, 0.1433],
                                     [0.8631, 0.2419], [1.13, 0.48],
                                     [1.0623, 0.7325], [0.8775, 0.9173],
                                     [0.625, 0.985], [0.3725, 0.9173],
                                     [0.1877, 0.7325], [0.12, 0.48],
                                     [0.1877, 0.2275], [0.3725, 0.0427],
                                     [0.625, -0.025], [0.8775, 0.0427],
                                     [1.0623, 0.2275]]), 4)

    # PA2 - Zoom 2
    pa2_fields = np.around(np.array([[-0.625000, 0.480000],
                                     [-0.456667, 0.480000],
                                     [-0.625000, 0.648333],
                                     [-0.793333, 0.480000],
                                     [-0.625000, 0.311667],
                                     [-0.288333, 0.480000],
                                     [-0.386941, 0.718059],
                                     [-0.625000, 0.816667],
                                     [-0.863059, 0.718059],
                                     [-0.961667, 0.480000],
                                     [-0.863059, 0.241941],
                                     [-0.625000, 0.143333],
                                     [-0.386941, 0.241941],
                                     [-0.120000, 0.480000],
                                     [-0.187657, 0.732500],
                                     [-0.372500, 0.917343],
                                     [-0.625000, 0.985000],
                                     [-0.877500, 0.917343],
                                     [-1.06234, 0.732500],
                                     [-1.13000, 0.480000],
                                     [-1.06234, 0.227500],
                                     [-0.877500, 0.0426571],
                                     [-0.625000, -0.0250000],
                                     [-0.372500, 0.0426571],
                                     [-0.187657, 0.227500]]), 4)

    # Additional 24 fields that were generated to try and further constrain position fits.
    pa2_addition_24_fields = np.around(np.array([[-0.219, 0.48],
                                                 [-0.27325971, 0.6825],
                                                 [-0.4215, 0.83074029],
                                                 [-0.624, 0.885],
                                                 [-0.8265, 0.83074029],
                                                 [-0.97474029, 0.6825],
                                                 [-1.029, 0.48],
                                                 [-0.97474029, 0.2775],
                                                 [-0.8265, 0.12925971],
                                                 [-0.624, 0.075],
                                                 [-0.4215, 0.12925971],
                                                 [-0.27325971, 0.2775],
                                                 [-0.26691108, 0.83708892],
                                                 [-0.49329638, 0.96779254],
                                                 [-0.75470362, 0.96779254],
                                                 [-0.98108892, 0.83708892],
                                                 [-1.11179254, 0.61070362],
                                                 [-1.11179254, 0.34929638],
                                                 [-0.98108892, 0.12291108],
                                                 [-0.75470362, -0.00779254],
                                                 [-0.49329638, -0.00779254],
                                                 [-0.26691108, 0.12291108],
                                                 [-0.13620746, 0.34929638],
                                                 [-0.13620746, 0.61070362]]), 4)

    # pa3_fields, generated with generateFields.py with radius of 0.455
    pa3_fields = np.around(np.array([[0, -0.75], [0.156667, -0.75],
                                     [-6.84812e-009, -0.570333],
                                     [-0.156667, -0.75],
                                     [1.86823e-009, -0.929667],
                                     [0.313333, -0.75], [0.22156, -0.495913],
                                     [-1.36962e-008, -0.390667],
                                     [-0.22156, -0.495913], [-0.313333, -0.75],
                                     [-0.22156, -1.00409],
                                     [3.73646e-009, -1.10933],
                                     [0.22156, -1.00409],
                                     [0.47, -0.75], [0.407032, -0.4805],
                                     [0.235, -0.283212],
                                     [-2.05444e-008, -0.211],
                                     [-0.235, -0.283212], [-0.407032, -0.4805],
                                     [-0.47, -0.75], [-0.407032, -1.0195],
                                     [-0.235, -1.21679],
                                     [5.60469e-009, -1.289], [0.235, -1.21679],
                                     [0.407032, -1.0195]]), 4)

    if array == 1:
        return pa1_fields
    elif array in [2, 5]:
        return pa2_fields
    elif array == -2:
        return pa2_addition_24_fields
    elif array in [3, 6]:
        return pa3_fields
    elif array == 4:
        return pa1_fields # PA4 is in PA1 position
    else:
        raise ValueError("Please pick either PA1 (1), PA2 (2), PA3 (3) or PA4 (4).")
