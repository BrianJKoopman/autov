#!/usr/bin/python2
# Brian Koopman
# ACTPol specific AutoV class.

import logging

from autov import AutoV, check_md5sums
from parse_seq import read_seq, parse_surface

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

        check_md5sums(clean_file_dir, md5sums)

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

    def decenter_surface(self, surface, parameter, offset):
        """Apply a "Basic" decenter to window, decentering entire cryostat.

        General: N

        Note, this is all in reference to the surfaces as they were defined in
        the original .seq file, no surface deletion/addition tracking is implimented
        yet, so autov doesn't know if you've changed surfaces at all.

        Units: ADE and BDE are in degrees, XDE, YDE, ZDE are in System Units.

        :param surface: Surface number in original .seq file to decenter.
        :type surface: int
        :param parameter: Parameter to decenter. This corresponds to any
                          decenter parameter in CODE V. We're focusing on x, y,
                          z, alpha and beta.
        :type parameter: str
        :param offset: Offset value, from current, for decenter in system units.
        :type offset: float

        """
        #TODO: Ugh, this needs to be broken up a bit I think, so that it's
        # decenter a general surface.
        parameter_lookup = {"x": "XDE", "y": "YDE", "z": "ZDE", "alpha": "ADE", "beta": "BDE"}
        decenter_command = parameter_lookup[parameter.lower()]

        if self.array in ['1', '2']:
            text = "! Apply Decenter to window clamp, decentering entire cryostat/optics tube.\n"
            window_clamp_surface = surface

            # Determine current value for decenter
            # TODO: For PA1, we set decenters. Should use parse the
            # surfaces before setting those and record these values as we set
            # them.
            seq_dict = parse_surface(read_seq(self.seq_file), window_clamp_surface)
            print seq_dict
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
        out_file = self._make_windows_out_file(filename)
        # Add ray trace file output to cfg_dict.
        dict_out_file = self._make_cfg_dict_out_file(filename)
        self.cfg_dict["codev_inputs"]["ray_trace"] = [dict_out_file]

        # Definte image_surface defaults or take alt_image
        if alt_image is 0:
            if self.array in ['1', '2', '3']:
                image_surface = 42
            elif self.array in ['4']:
                image_surface = 47
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
