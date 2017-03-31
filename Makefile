
.PHONY : symlinks
symlinks : 
	ln -s /home/koopman/lab/output/autov output

.PHONY : clean
clean :
	rm -f output

# vim: set expandtab!:
