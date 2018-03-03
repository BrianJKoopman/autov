=========================
Polarization Calibration
=========================
`autov` plays a key role in the polarization calibration for ACTPol. Running
`autov` is, infact, the first step in this process. This will produce the
appropriate `psf`, `poldsp`, and `RSI` output from CODEV for calibration as
well as a configuration file which provides details on the parameters used in
`autov`. This form an input later used by codevpol's calibration process.

-----------
bin/polcal/
-----------
With in `autov/bin/polcal/` there are several scripts, a configuration file and
a Makefile.

polcal_ar1234.py
----------------
This script automates the whole CODEV pipeline (for arrays 1, 2, 3, and 4). It
will output a template configuration file with the paths for all of its output
files for use later in calibrating.

check_setup.py
--------------
Used to manually check the CODE V automated setup. Will do all the
configuration done in polcal.py but not excecute any of the analyses or exit
the program. This will allow you to click around and check to make sure
everything is setup properly for automation.

To run:

.. code-block:: bash

    python check_setup.py 5 150

This will load up a lens file for ar5 at 150 GHz.
