# Variables
CODEVPOL_CAL_CFG_DIR = /home/koopman/git/codevpol/bin/cfg/calibration/

# Patterns
TMP_AUTOV_CONFIGS = $(wildcard ../output/calibration/*.in)
#AUTOV_CONFIGS = $(wildcard *.in)
AUTOV_CONFIGS = $(patsubst ../output/calibration/%.in, %.in, $(TMP_AUTOV_CONFIGS))
CODEVPOL_CONFIG_DUMMIES = $(wildcard $(CODEVPOL_CAL_CFG_DIR).*.dummy)
CODEVPOL_CONFIGS = $(patsubst %.in, $(CODEVPOL_CAL_CFG_DIR).%.in.dummy, $(AUTOV_CONFIGS))
CODEVPOL_CONFIG_OUTPUT = $(wildcard $(CODEVPOL_CAL_CFG_DIR)*.json)
#CODEVPOL_CONFIG_OUTPUT_YEARS = $(wildcard $(CODEVPOL_CAL_CFG_DIR)20*)

# Targets
.PHONY : codevpol_cal_cfg
codevpol_cal_cfg : $(CODEVPOL_CONFIGS)

#$(CODEVPOL_CAL_CFG_DIR).cfg_calibration_pa1_150ghz.in.dummy : cfg_calibration_pa1_150ghz.in
#	python2 add_to_config.py $^ 2013
#	touch $(CODEVPOL_CAL_CFG_DIR).cfg_calibration_pa1_150ghz.in.dummy

# Note this targets a dummy file, which relates to the dep of the autov output
# .in files. This is because we try to run for every year, which doesn't always
# exist, producing an unreliable target, so instead we make this empty dummy
# file.
$(CODEVPOL_CAL_CFG_DIR).%.in.dummy : ../output/calibration/%.in codevpol_pointing_metadata.json add_to_config.py
	python2 add_to_config.py $< 2013
	python2 add_to_config.py $< 2014
	python2 add_to_config.py $< 2015
	python2 add_to_config.py $< 2016
	#python2 add_to_config.py $< 2017
	touch $@

## variables   : Print variables.
.PHONY : variables
variables:
	@echo TMP_AUTOV_CONFIGS: $(TMP_AUTOV_CONFIGS)
	@echo AUTOV_CONFIGS: $(AUTOV_CONFIGS)
	@echo CODEVPOL_CONFIGS: $(CODEVPOL_CONFIGS)
	@echo CODEVPOL_CONFIG_DUMMIES: $(CODEVPOL_CONFIG_DUMMIES)
	@echo CODEVPOL_CONFIG_OUTPUT: $(CODEVPOL_CONFIG_OUTPUT)
	#@echo CODEVPOL_CONFIG_OUTPUT_YEARS: $(CODEVPOL_CONFIG_OUTPUT_YEARS)

.PHONY : symlinks
symlinks :
	#if [ ! -L RelativeOffsets ]; then ln -s /home/koopman/github/actpol_data_shared/RelativeOffsets RelativeOffsets; fi
	#if [ ! -L img ]; then ln -s /home/koopman/lab/output/codevpol/plots img; fi
	#if [ ! -L pkl ]; then ln -s /home/koopman/tmp/codevpol/pkl pkl; fi

.PHONY : clean
clean :
	@#rm -f $(CODEVPOL_CONFIGS)
	@#rm -f $(CODEVPOL_CONFIG_DUMMIES)
	@#rm -f $(CODEVPOL_CONFIG_OUTPUT)
	#@#rm -rf $(CODEVPOL_CONFIG_OUTPUT_YEARS)
	rm -f $(CODEVPOL_CONFIGS)
	rm -f $(CODEVPOL_CONFIG_DUMMIES)
	rm -f $(CODEVPOL_CONFIG_OUTPUT)
	#rm -rf $(CODEVPOL_CONFIG_OUTPUT_YEARS)

# vim: set expandtab!:
