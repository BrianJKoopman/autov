
.PHONY : symlinks
symlinks : 
	if [ ! -L ./bin/output ]; then ln -sT /home/koopman/lab/output/autov/ ./bin/output; fi
	if [ ! -L ./bin/log ]; then ln -sT /home/koopman/lab/output/log/autov/ ./bin/log; fi

.PHONY : clean
clean :
	rm -f ./bin/output
	rm -f ./bin/log
	rm -f *.rec

# vim: set expandtab!:
