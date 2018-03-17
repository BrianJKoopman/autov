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
import hashlib
import numpy as np

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
        # General, shared AutoV instance attributes
        self.seq_file = None

        self.date = time.strftime('%Y%m%d')
        self.ctime = int(time.time())

        self.wl_set = False # have wavelengths been set yet?
        self.wavelengths = None # save wavelengths after setting

        #: A string describes the ACTPol array number.
        self.array = array

        #: A list of strings which will be written sequentially to the name of output files.
        self.descriptors = descriptors
        self.seq = []

        self.out_dir = r"E:\ownCloud\optics\data" + "\\"
        self.tmp_dir = r"E:\ownCloud\optics\data\tmp" + "\\"

        #: Dictionary containing information to be written to a codevpol style cfg file.
        self.cfg_dict = {"array": int(self.array),
                         "codev_inputs": {}
                        }

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

        if len(wavelengths) < 3:
            # If we're setting just one wavelength, delete two set wavelengths first.
            text += "DEL W0+1\n"
            text += "DEL W0+1\n"

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
            self.cfg_dict["codev_inputs"]["freq"] = int(lambda2freq(wavelengths[reference]))
            self.descriptors.append("%03d"%int(lambda2freq(wavelengths[reference])) + "ghz")

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

    def quick_best_focus(self, force=False):
        """Perform two quick best focuses.

        General: Y
        """
        if not force:
            raise RuntimeError("Throwing this because you shouldn't be using quick_best focus.")
        else:
            text = "! quick best focus, twice\n"
            text += "WAV ; BES; RFO; GO\n"
            text += "WAV ; BES; RFO; GO\n"
            logging.info("Performing a quick best focus, twice")
            self.seq.append(text)
            logging.debug("Adding text to .seq file: \n%s", text)
            return text

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
        file_name = "%scfg"%(out_dir)
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

    def delete_solve(self, surface):
        """Remove the solve on a surface, probably used for removing a solve on
        a lens thickness.

        General: Y
        """
        text = "! Delete solve on S%s\n"%(surface)
        text += "DEL SOL THI S%s\n"%(surface)
        self.seq.append(text)
        return text

    def freeze_surface(self, surface):
        """Freeze a surface

        General: Y
        """
        text = "! Freeze S%s\n"%(surface)
        text += "THC S%s 100\n"%(surface)
        self.seq.append(text)
        return text

    # Tolerancing methods (pulled from autoccatp)
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

    # TODO: need to write cleanup method for rm'ing the tmp directory. ccatp had 16,000 tmp files.
    def save_lens(self, filename):
        """Save the lens file to temporary location for running tolfdif."""
        text = "! Save lens file\n"
        text += "SAV \"%s\"\n"%(filename)
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

SPEED_OF_LIGHT = 299792458. # [m/s]

def lambda2freq(wavelength):
    """Convert from wavelength to frequency.

    Keeping CODEV in mind, wavelengths in CODEV are in nm and we want GHz.

    Args:
        wavelength (float): wavelength in nm

    Returns:
        freq (float): Frequency in GHz
    """
    return SPEED_OF_LIGHT/wavelength #[GHz]

def freq2lambda(freq):
    """Convert from frequency to wavelength.

    Keeping CODEV in mind, wavelengths in CODEV are in nm and we think in GHz.

    Args:
        freq (float): Frequency in GHz

    Returns:
        wavelength (float): wavelength in nm
    """
    return SPEED_OF_LIGHT/freq #[nm]

def check_md5sums(clean_file_dir, md5sums_list):
    """Check a file against a known list of md5sums for a match.

    :param clean_file_dir: Directory the clean files are kept in
    :type clean_file_dir: str
    :param m5sums_list: Dictionary of md5sums with filenames for keys and md5sums as values
    :type md5sums_list: dict

    :return: True, since if it finishes without raising an error, all md5sums match.
    :rtype: boolean
    """
    for item in md5sums_list.keys():
        md5 = hashlib.md5(open(clean_file_dir + item, 'rb').read()).hexdigest()
        if md5 != md5sums_list[item]:
            logging.critical("md5sum mis-match: %s", item)
            logging.critical("Mis-match indicates a dirty starting file. Please examine.")
            raise RuntimeError("The md5sum does not match a known value! \
                  This means a 'clean' file has been modified! Exiting.")
        else:
            logging.info("md5sum match: %s", item)
            logging.info("Match indicates file unmodified, proceeding with script.")

    return True


#class AutoMul(object):
#    def __init__(self):
#    def
