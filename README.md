autov - Automated Code V Sequence File Generation
==================================================

`autov` was built to generate Code V sequence files to run automated analyses
of existing optical designs.

Motivation
----------

While analyzing the ACTPol optical design for work related to the polarization
calibration of telescope I noted several things about using Code V:

* I would need to run analyses I had been accessing via a GUI multiple times
* I should always start from a `clean` copy of the design I was working on, you
  can't be sure something wasn't changed in the GUI already, leading to
  unreproducible results
* The Code V Macro-PLUS language is difficult to read

This lead me to try automating my analyses, and I concluded that writing a
wrapper in python seemed easier than learning to read the Macro-PLUS language.

I built `autov` to write out commands that I wanted to run, into a `.seq` file,
which I'd then call via something like cygwin to run in Code V. This enabled me
to run complex analyses with different inputs, saving output to a file which
could be processed later.

# Computing Environment
I mostly use a Linux environment, however Code V only runs on Windows. While
not officially supported, I've found Code V runs fine in a virtual machine.

My setup consists of:

* Arch Linux host
* Windows 7 guest
* cygwin (or other terminal emulator) on the Windows guest
* Shared folders between the guest and host

This allows me to develop code on the Linux host, install any developed python
packages on the Windows guest, run code on the Windows guest, and process
output on the Linux host.

I have not explored the use of the Linux subsystem for Windows on Windows 10,
though it sounds like an appealing way to run this if you have access to it.

# Flexibility
I didn't start writing this code with sharing in mind (sorry!). As a result,
it's probably not very flexible in terms of moving systems. There's a lot of
hardcoded paths which relate to the filesystem layout on my Windows guest that
will need adjustment on any other system. Ideally these would get changed to be
within a configurable directory.

## Telescope Specific Code
I originally only focused on an existing telescope design, where many of the
operations I was performing were specific to that design, i.e. changing
coatings on a particular surface. This lead to an API that had telescope design
specific commands, rather than general commands for i.e. changing coatings on a
given surface.

As I started to work on different telescope designs, performing similar
analyses, I split these telescope specific designs into different modules.
General commands should be in `autov.py`, while telescope specific designs are
in, i.e. `autoact.py` for the ACT telescope designs, `autoso.py` for the Simons
Observatory telescope design, and `autoccatp.py` for the CCATp telescope
design.

# Parsing Input `.seq` Files
Part of the difficulty with using a wrapper, is the lack of access to already
set variables. For instance, if one wants to test the effect of an offset in
the position of an optical element on the Strehl ratio, it is useful to obtain
the current position of the optical element. For this we need to parse the
input lens file.

I've written some code to extract specific parts of `.seq` files in
`parse_seq.py`. However, this doesn't get all information from the input
design.

Installation
------------

Simply clone the repository:

```bash
$ git clone https://github.com/BrianJKoopman/autov.git
```

Then we can use `pip` to install the code on our Windows guest.

```bash
$ cd /path/to/autov/
$ pip install -e . --user
```

# Documentation
We use sphinx for our documentation. You can build the (sparse) documentation
by entering the `docs/` directory and running:

```bash
$ make html
```

Usage
-----

User scripts are located in `./bin/`, and can be called after installation of
the `autov` package.

Often I'll write a quick bash script like `run.sh` to run with a bunch of
different inputs.


Contributing
------------

1. Check the open issues or open a new issue to start a discussion around
   your feature idea or the bug you found
2. Fork the repository and make your changes
3. Send a pull request
