
.PHONY : symlinks
symlinks : 
	if [ ! -L output ]; then ln -sT /home/koopman/lab/output/autov/ output; fi
	if [ ! -L log ]; then ln -sT /home/koopman/lab/output/log/autov/ log; fi

.PHONY : clean
clean :
	rm -f output
	rm -f log
	rm -f *.rec

# vim: set expandtab!:
