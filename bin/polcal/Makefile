# Variables
CODEVPOL_CAL_CFG_DIR = /home/koopman/git/codevpol/bin/cfg/calibration/

# Patterns
TMP_AUTOV_CONFIGS = $(wildcard ../output/calibration/*.in)
#AUTOV_CONFIGS = $(wildcard *.in)
AUTOV_CONFIGS = $(patsubst ../output/calibration/%.in, %.in, $(TMP_AUTOV_CONFIGS))
CODEVPOL_CONFIG_DUMMIES = $(wildcard $(CODEVPOL_CAL_CFG_DIR).*.dummy)
CODEVPOL_CONFIGS = $(patsubst %.in, $(CODEVPOL_CAL_CFG_DIR).%.in.dummy, $(AUTOV_CONFIGS))
CODEVPOL_CONFIG_OUTPUT = $(wildcard $(CODEVPOL_CAL_CFG_DIR)*.json)

# polcal targets these files, which are output by polcal_ar1234.py and form
# inputs for codevpol code
POLCAL_IN_FILES = cfg_calibration_pa1_150ghz.in \
				  cfg_calibration_pa2_150ghz.in \
			      cfg_calibration_pa3_090ghz.in cfg_calibration_pa3_150ghz.in \
			      cfg_calibration_pa4_150ghz.in cfg_calibration_pa4_220ghz.in \
				  cfg_calibration_pa5_090ghz.in cfg_calibration_pa5_150ghz.in \
				  cfg_calibration_pa6_090ghz.in cfg_calibration_pa6_150ghz.in
POLCAL_CFG_LOCATION = ../output/calibration/
POLCAL_TARGETS = $(addprefix $(POLCAL_CFG_LOCATION), $(POLCAL_IN_FILES))

# Targets
# To be run externally by codevpol (could setup locally if symlink
# actpol_data_shared properly)
.PHONY : codevpol_cal_cfg
codevpol_cal_cfg : $(CODEVPOL_CONFIGS)

.PHONY : polcal
polcal : $(POLCAL_TARGETS)

# pa1
$(POLCAL_CFG_LOCATION)cfg_calibration_pa1_150ghz.in : polcal_ar1234.py
	python polcal_ar1234.py 1 150

# pa2
$(POLCAL_CFG_LOCATION)cfg_calibration_pa2_150ghz.in : polcal_ar1234.py
	python polcal_ar1234.py 2 150

# pa3
$(POLCAL_CFG_LOCATION)cfg_calibration_pa3_090ghz.in : polcal_ar1234.py
	python polcal_ar1234.py 3 90

$(POLCAL_CFG_LOCATION)cfg_calibration_pa3_150ghz.in : polcal_ar1234.py
	python polcal_ar1234.py 3 150

# pa4
$(POLCAL_CFG_LOCATION)cfg_calibration_pa4_150ghz.in : polcal_ar1234.py
	python polcal_ar1234.py 4 150

$(POLCAL_CFG_LOCATION)cfg_calibration_pa4_220ghz.in : polcal_ar1234.py
	python polcal_ar1234.py 4 220

# pa5
$(POLCAL_CFG_LOCATION)cfg_calibration_pa5_090ghz.in : polcal_ar1234.py
	python polcal_ar1234.py 5 90

$(POLCAL_CFG_LOCATION)cfg_calibration_pa5_150ghz.in : polcal_ar1234.py
	python polcal_ar1234.py 5 150

# pa6
$(POLCAL_CFG_LOCATION)cfg_calibration_pa6_090ghz.in : polcal_ar1234.py
	python polcal_ar1234.py 6 090

$(POLCAL_CFG_LOCATION)cfg_calibration_pa6_150ghz.in : polcal_ar1234.py
	python polcal_ar1234.py 6 150

# Note this targets a dummy file, which relates to the dep of the autov output
# .in files. This is because we try to run for every year, which doesn't always
# exist, producing an unreliable target, so instead we make this empty dummy
# file.
$(CODEVPOL_CAL_CFG_DIR).%.in.dummy : ../output/calibration/%.in codevpol_pointing_metadata.json add_to_config.py
	python2 add_to_config.py $< 2013
	python2 add_to_config.py $< 2014
	python2 add_to_config.py $< 2015
	python2 add_to_config.py $< 2016
	python2 add_to_config.py $< 2017
	touch $@

## variables   : Print variables.
.PHONY : variables
variables:
	@echo TMP_AUTOV_CONFIGS: $(TMP_AUTOV_CONFIGS)
	@echo AUTOV_CONFIGS: $(AUTOV_CONFIGS)
	@echo CODEVPOL_CONFIGS: $(CODEVPOL_CONFIGS)
	@echo CODEVPOL_CONFIG_DUMMIES: $(CODEVPOL_CONFIG_DUMMIES)
	@echo CODEVPOL_CONFIG_OUTPUT: $(CODEVPOL_CONFIG_OUTPUT)
	@echo POLCAL_TARGETS: $(POLCAL_TARGETS)

.PHONY : symlinks
symlinks :
	@#if [ ! -L RelativeOffsets ]; then ln -s /home/koopman/github/actpol_data_shared/RelativeOffsets RelativeOffsets; fi
	@#if [ ! -L img ]; then ln -s /home/koopman/lab/output/codevpol/plots img; fi
	@#if [ ! -L pkl ]; then ln -s /home/koopman/tmp/codevpol/pkl pkl; fi

.PHONY : clean
clean :
	@#rm -f $(CODEVPOL_CONFIGS)
	@#rm -f $(CODEVPOL_CONFIG_DUMMIES)
	@#rm -f $(CODEVPOL_CONFIG_OUTPUT)
	rm -f $(CODEVPOL_CONFIGS)
	rm -f $(CODEVPOL_CONFIG_DUMMIES)
	rm -f $(CODEVPOL_CONFIG_OUTPUT)

# vim: set expandtab!:
