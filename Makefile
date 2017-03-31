
.PHONY : symlinks
symlinks : 
	ln -s /home/koopman/lab/output/autov output

.PHONY : clean
clean :
	rm -f output
	rm -f *.rec

# vim: set expandtab!:
