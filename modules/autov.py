#!/usr/bin/python2
# Brian Koopman
"""Module for helping autov functions."""

#TODO: best bet for descriptive info in file output is to continue ! comments with some pattern to extract later
# serially increment output text files and have a descriptive directory structure?
# my concern with dating and ctiming output was archiving, but I honestly never go back and look
# I think the Makefile archiving scheme outlined in that tutorial would help solve this....

import subprocess
import os
import time
import json
import logging
import numpy as np

from modules.codey import get_fields
from modules.parse_seq import read_seq, parse_surface

class AutoV(object):
    """Class for writing custom .seq files for automating CODEV.

    The methods in this class will append the appropriate text for writing a
    .seq file which can be called by CODEV and used to automate testing
    parameters in a lens design.

    :param array: Which ACTPol array we're automating
    :type array: str
    :param descriptors: List of file descriptors to append in file names.
                        Called by most (all?) methods which output files.
    :type descriptors: :obj:`list` of :obj:`str`
    """
    def __init__(self, array, descriptors):
        #: A string describes the ACTPol array number.
        self.array = array

        #: A list of strings which will be written sequentially to the name of output files.
        self.descriptors = descriptors
        self.seq = []

        self.seq_file = None

        self.out_dir = r"E:\ownCloud\optics\data" + "\\"
        self.tmp_dir = r"E:\ownCloud\optics\data\tmp" + "\\"

        self.date = time.strftime('%Y%m%d')
        self.ctime = int(time.time())

        self.wl_set = False # have wavelengths been set yet?
        self.wavelengths = None # save wavelengths after setting

        #: Dictionary containing information to be written to a codevpol style cfg file.
        _out_dir = '/home/koopman/ownCloud/niemack_lab/analysis/codevpol/img/'
        _data_dir = '/home/koopman/ownCloud/niemack_lab/optics/data/'
        self.cfg_dict = {"array": int(self.array),
                         "directories": {"outDir": _out_dir,
                                         "data_dir": _data_dir},
                         "codev_inputs": {"freq": [145]}
                        }

        # More array dependant setup for cfg_dict.
        if self.array in ["2"]:
            self.cfg_dict["offset_file"] = "./data/season3_positions/template_ar2_150529s.txt"
        elif self.array in ["4"]:
            self.cfg_dict["offset_file"] = "./actpol_data_shared/" \
                                           "RelativeOffsets/template_ar4_160830.txt"


    def create_header(self):
        """Create header comments for the .seq file.

        General: Y

        :return: header text
        :rtype: str
        """
        # TODO: Add parameters to the header, which array, etc. anything in __init__.
        header = "! This .seq file was created by the AutoV automation class. \n"
        header += "! How to run me: " + \
                  r"C:\CODEV105_FCS\codev.exe E:\ownCloud\optics\autov\seq\script.seq" + "\n"
        logging.debug("Adding text to .seq file: \n%s", header)
        self.seq.append(header)
        return header

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

    def remove_surface(self, surface):
        """Remove specified surface from lens data manager.

        General: Y

        :param surface: surface number in lens data manager to remove
        :type surface: int
        :return: text which removes the surface
        :rtype: str
        """
        text = "! Removing Surface %s \n"%(int(surface))
        text += "DEL S%s"%(int(surface))
        self.seq.append(text)
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def remove_field(self, field):
        """Remove specified surface from lens data manager.

        General: Y

        :param field: field number in system data fields to remove
        :type field: int
        :return: text which removes the field
        :rtype: str
        """
        text = "! Removing Field %s \n"%(int(field))
        text += "DEL F%s+1"%(int(field)-1)
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

    def set_wavelengths(self, wavelengths, reference):
        """Set the wavelengths in CODEV.

        General: N
        TODO: Assumes 3 wavelengths already set.

        For studies that are wavelength dependant we need only a single WL to
        have weight 1, the rest 0. We set the reference wavelength to 1 and the
        rest to 0. So we always need both arguments.

        Warning:
        There are some pretty subtle difficulties with setting a bunch of
        wavelengths and then changing those wavelengths. Your best off setting
        all the wavelengths you want in the first call and not changing them,
        only passing the same set of wavelengths with a different reference
        number to change the REF and weight of the REF WL.

        :param wavelengths: list of wavelengths, max length is 21
        :param reference: change what the reference wavelength is (note,
                          indexed on 0). The reference is used to change the
                          weight of the called wavelength to 1, the rest to 0.
        """
        if wavelengths is None:
            raise ValueError("No wavelenth specified, presumably just changing reference.")
        else:
            if len(wavelengths) > 21:
                logging.critical("More than 21 wavelength passed in wavelengths argument, 21 is the max supported by Code V.")
                raise ValueError("More than 21 wavelengths submitted, this is too many.")
            if len(wavelengths) != len(np.unique(wavelengths)):
                raise ValueError("Wavelengths submitted not unique, please remove duplicates.")

        if self.wl_set is True:
            if len(wavelengths) != len(self.wavelengths):
                raise ValueError("Specify same number of wavelengths for each function call.")

        text = "! modify wavelengths\n"

        for wavelength in wavelengths:
            if wavelengths.index(wavelength) > 2:
                # always skip first 3, which are set in both clean copies
                if self.wl_set == False:
                    text += "IN CV_MACRO:inswl %s+1\n"%(wavelengths.index(wavelength))
            if self.wl_set is False:
                text += "WL W%s %s\n"%(wavelengths.index(wavelength)+1, wavelength)
            if wavelengths.index(wavelength) is 0:
                text += "WTW W1 1\n" # always need a WL set to 1, make it the first
            if wavelengths.index(wavelength) is not 0:
                text += "WTW W%s 0\n"%(wavelengths.index(wavelength)+1) # set others to 0

            logging.info("Wavelengths set to %s", wavelengths)

        if reference is not None:
            text += "REF %s\n"%(reference+1)
            text += "WTW W%s 1\n"%(reference+1) # Change the weight of ref to 1

            if reference is not 0:
                text += "WTW W1 0\n" # set WL1 weight to 0 if it's not the ref

            logging.info("Reference wavelength set to %s", wavelengths[reference])
            self.seq.append(text)

        self.wl_set = True
        self.wavelengths = wavelengths

        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def set_vignetting(self):
        """Run the default set vignetting command in CODEV.

        General: Y
        """
        text = "! set vignetting\n"
        text += "run " + r"C:\CODEV105_FCS\macro\setvig.seq" + " 1e-007 0.1 100 NO ;GO\n"
        self.seq.append(text)
        logging.info("Vignetting set")
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def activate_pol_ray_trace(self):
        """Active polarization ray tracing.

        General: Y
        """
        text = "! activate polarization ray tracing\n"
        text += "POL YES\n"
        self.seq.append(text)
        logging.info("Polarization sensitive ray trace enabled")
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
        if _array in ['2', '3']:
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

    def quick_best_focus(self, force=False):
        """Perform two quick best focuses.

        General: Y
        """
        if not force:
            raise RuntimeError("Throwing this because you shouldn't be using quick_best focus.")
        else:
            """Insert two quick best focus commands."""
            text = "! quick best focus, twice\n"
            text += "WAV ; BES; RFO; GO\n"
            text += "WAV ; BES; RFO; GO\n"
            logging.info("Performing a quick best focus, twice")
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
        #TODO: Ugh, this needs to be broken up a bit I think, so that it's decenter a general surface.
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
        #TODO: Ugh, this needs to be broken up a bit I think, so that it's decenter a general surface.
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

    # TODO: maybe make these not class methods and pass in descriptors, since
    # we could be making a windows outfile separate from the class...
    def _make_windows_out_file(self, filename):
        out_file = "%s%s\\%s_%s"%(self.out_dir, self.date, self.ctime, filename)
        for descriptor in self.descriptors:
            out_file += "_%s"%(descriptor)
        out_file += "_ar%s.txt"%(self.array)
        return out_file

    def _make_cfg_dict_out_file(self, filename):
        dict_out_file = "%s/%s_%s"%(self.date, self.ctime, filename)
        for descriptor in self.descriptors:
            dict_out_file += "_%s"%(descriptor)
        dict_out_file += "_ar%s.txt"%(self.array)
        return dict_out_file

    def run_psf(self):
        """Run the point spread function commands.

        General: Y

        Will output psf results to a tmp file, psf.txt which will be moved by
        the user later for permanent storage."""
        # TODO: make a method for storing temporary files, rather than having
        # the user worry about it.
        # Can't have file name with any .'s other than in .txt
        filename = "psf"
        out_file = self._make_windows_out_file(filename)
        logging.info("Saving psf output to %s", out_file)
        # Add psf file output to cfg_dict.
        dict_out_file = self._make_cfg_dict_out_file(filename)
        self.cfg_dict["codev_inputs"]["psf"] = dict_out_file

        text = "! auto_psf.seq\n"
        text += "OUT " + out_file + " ! Sets output file\n"
        text += "! Script generated by PSF GUI interface.\n"
        text += "PSF; CAN;\n"
        text += "PSF\n"
        text += "TGR 1024\n"
        text += "PGR 1024\n"
        text += "NRD 51\n"
        text += "COM YES\n"
        text += "LIS NO\n"
        text += "PLO NO\n"
        text += "DIS NO\n"
        text += "GO\n"
        text += "OUT T ! Restores regular output\n"
        self.seq.append(text)
        logging.info("PSF .seq inserted")
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

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

    def run_poldsp(self, input_angle, pupil_number=11):
        """Run the poldsp macro for polarization studies.

        General: N
        TODO: Currently assumes 25 fields.

        :param input_angle: Sets the field orientation angle at the input for
                            all fields.
        :param filename: Set the filename for temporary output. This is likely
                         to want to change based on input angle.
        :param pupil_number: Number of rays across the pupil diameter.
        """
        # TODO: This also wants to know about the fields set
        filename = "poldsp_%sdeg"%(str(int(input_angle)))
        out_file = self._make_windows_out_file(filename)
        # Add poldsp file output to cfg_dict.
        dict_out_file = self._make_cfg_dict_out_file(filename)
        self.cfg_dict["codev_inputs"]["poldsp_%sdeg"%(str(int(input_angle)))] = [dict_out_file]

        text = "! Set input field orientation\n"
        for i in range(25):
            text += "POR F%s %s\n"%((i+1), input_angle)

        #text += "OUT " r"E:\owncloud\optics\data\tmp" + "\\" + filename + " ! Sets output file\n"
        text += "OUT " + out_file + " ! Sets output file\n"
        text += "RUN " r"C:\CODEV105_FCS\macro\poldsp.seq" + \
                " 0 %s \"Polarization State\" \"Full\"\n"%(pupil_number)
        text += "OUT T ! Restores regular output\n"
        self.seq.append(text)
        logging.info("poldsp .seq inserted")
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def enter_single_command(self, command):
        """Enter single command in event I don't have a method for it.

        General: Y
        """
        text = "! Manual command entry\n"
        text += "%s\n"%(command)
        self.seq.append(text)
        logging.info("Single Command '%s' inserted", command)
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def exit(self):
        """Exit from CODEV without prompt.

        General: Y
        """
        text = "! exit without prompt when finished\n"
        text += "exit y\n"
        self.seq.append(text)
        logging.info("Exit .seq inserted")
        logging.debug("Adding text to .seq file: \n%s", text)
        return text

    def _write_seq(self):
        """Write the master CODEV sequence file.

        This will always write to the same autov.seq file, which will get moved permanently

        Keyword arguments:
        inputs -- list of input strings
        seqfile -- name of output .seq file"""

        # CODE V will choke on a complicated filename, we need to keep it
        # simple and move the file later for saving.
        seqfile = "E:\ownCloud\optics\\autov\seq\\autov.seq"
        # seqfile = "%s%s\\%s_autov.seq.pa%s"%(self.out_dir, self.date, self.ctime, self.array)

        with open(seqfile, 'w') as f:
            for item in self.seq:
                f.write(item)
                f.write('\n')

        return seqfile

    def _move_seq(self):
        # # Move automation .seq file for permanent record
        filename = "autov"
        seqfile = "%s%s\\%s_%s"%(self.out_dir, self.date, self.ctime, filename)
        if self.descriptors is not None:
            for descriptor in self.descriptors:
                seqfile += "_%s"%(descriptor)
        seqfile += "_ar%s.seq"%(self.array)

        print "mv E:\ownCloud\optics\\autov\seq\\autov.seq %s"%(seqfile)
        subprocess.call("mv E:\ownCloud\optics\\autov\seq\\autov.seq %s"%(seqfile))

        return seqfile

    def _call_codev(self, seqfile):
        """Make the call to CODE V."""
        # Make the CODEV Call
        logging.info("Calling codev.exe")
        subprocess.call("C:\CODEV105_FCS\codev.exe %s"%seqfile)

    def run(self):
        """Write then run the .seq file.

        General: Y
        """
        seqfile = self._write_seq() # write

        # Check for existence of output directory before writing.
        check_dir("%s%s"%(self.out_dir, self.date))

        self._call_codev(seqfile) # run
        self._move_seq() # move


    def add_to_json_cfg(self, key, value):
        """Add to the dictionary that we'll be dumping to a JSON configuration file.

        :param key: The key in the dictionary to be dumped to JSON config file.
        :type key: str
        :param value: The value for the associated key in the dictionary to be dumped to JSON config file.
        :type value: any valid dictionary value
        """
        self.cfg_dict[key] = value

    def save_cfg(self, out_dir="./output/"):
        """Save the configuration dictionary for use with codevpol.

        Check the directory with check_dir before outputting.

        General: Y

        :param out_dir: Output directory, end with a /.
        :type out_dir: str
        """
        check_dir(out_dir)
        file_name = "%scfg_ar%s"%(out_dir, self.array)
        for descriptor in self.descriptors:
            file_name += "_%s"%(descriptor)
        file_name += ".in"
        with open(file_name, 'w') as f:
            f.write("extract = ")
            json.dump(self.cfg_dict, f)

    def set_buffer_len(self, length):
        """Change the length of B0, the default buffer.

        General: Y
        """
        text = "! Change B0 length\n"
        text += "BUF LEN %s\n"%(length)
        self.seq.append(text)
        return text

def byteify(input):
    # https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python/13105359#13105359
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def check_dir(directory):
    """Check if the directory exists, if not, create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info("Checking directory %s", directory)

def readseq(seqfile):
    """Read a CODEV sequence file, for use in combining a master .seq for
       automation."""
    with open(seqfile, 'r') as f:
        read_data = f.read()

    return read_data

SPEED_OF_LIGHT = 299792458 # [m/s]

def lambda2freq(wavelength):
    """Convert from wavelength to frequency.

    Keeping CODEV in mind, wavelengths in CODEV are in nm and we want GHz.

    Args:
        wavelength (float): wavelength in nm

    Returns:
        freq (float): Frequency in GHz
    """
    return SPEED_OF_LIGHT/float(wavelength) #[GHz]

def freq2lambda(freq):
    """Convert from frequency to wavelength.

    Keeping CODEV in mind, wavelengths in CODEV are in nm and we think in GHz.

    Args:
        freq (float): Frequency in GHz

    Returns:
        wavelength (float): wavelength in nm
    """
    return SPEED_OF_LIGHT/float(freq) #[nm]

#class AutoMul(object):
#    def __init__(self):
#    def
