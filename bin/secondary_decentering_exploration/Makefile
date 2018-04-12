ANALYSIS = secondary_decentering_exploration

AUTOV_OUTPUT_DIR = /home/koopman/lab/output/autov/$(ANALYSIS)/
CODEVPOL_INPUT_DIR = $(AUTOV_OUTPUT_DIR)codevpol_inputs/

AUTOV_OUTPUT_FILES = $(wildcard ./output/*.in)
CODEVPOL_INPUT_FILES = $(patsubst ./output/%.in, $(CODEVPOL_INPUT_DIR)%_2017.json, $(AUTOV_OUTPUT_FILES))

.PHONY : codevpol_inputs
codevpol_inputs : $(CODEVPOL_INPUT_FILES)

# Study the latest season, just 2017.
$(CODEVPOL_INPUT_DIR)%_2017.json : $(AUTOV_OUTPUT_DIR)%.in add_to_config.py
	python2 add_to_config.py $< 2017

.PHONY : variables
variables:
	@echo AUTOV_OUTPUT_DIR: $(AUTOV_OUTPUT_DIR)
	@echo AUTOV_OUTPUT_FILES: $(AUTOV_OUTPUT_FILES)
	@echo CODEVPOL_INPUT_DIR: $(CODEVPOL_INPUT_DIR)
	@echo CODEVPOL_INPUT_FILES: $(CODEVPOL_INPUT_FILES)

.PHONY : symlinks
symlinks : 
	if [ ! -L output ]; then ln -sT $(AUTOV_OUTPUT_DIR)secondary_decentering_exploration output; fi

.PHONY : clean
clean :
	rm -f output
	rm -f *.rec

# vim: set expandtab!:
