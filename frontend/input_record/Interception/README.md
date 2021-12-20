Interception
============

[Download the latest release][latest-release]

Building
--------

Source code is built upon [Windows Driver Kit Version 7.1.0][wdk].

Simple build scripts (`buildit.cmd`) are provided to build using specific build
environments of the WDK, they require the environment variable `%WDK%` to be
previously set to the WDK installation directory.

- Tested from Windows XP to Windows 10.

Driver installation
-------------------

Drivers can be installed through the command line installer, but driver
installation requires execution inside a prompt with administrative rights.

Run `install-interception` without any arguments inside an console executed as
administrator and it will give instructions for installation.
