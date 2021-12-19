







## Keyboard and Mouse Recording
For this project I will use AutoHotPy, it is a scripting tool, just like AutoHotKey, but it uses Interception library (https://github.com/oblitum/Interception).
The great thing is that Interception uses a very low level driver to capture keyboard and mouse events, which makes it perfect for games that have problems with AutoHotKey

## Installation
AutoHotPy doesn't really need any. You just place the scripts in the same folder and they just work. However, the libraries needed for it to run are not installed by default in any operative system.

1.    Verify you have Python installed
2.    Install interception driver (and restart your computer): http://oblita.com/Interception.html
hint: if double clicking in the executable doesn't install the driver (you will see an error message when you start AutoHotPy), try running a command line as administrator from the windows menu (right clicking on the program and selecting "Run as administrator"), and then go to your download location from the command line and run "install-interception.exe /install"
3.    Place the .dll in the same place were you downloaded AutoHotPy. We need interception.dll to work!


To use AutoHotPy you only have to write a script and place it in the same folder where you installed the app.


## Running the scripts

To run any of the scripts open a command line and run "python <yourscript>.py". That's all you need.



```
python macro.py
```

```
---- Hello to Macro----
Press F1 to start/stop macro
Press F2 to start macro
Press F3 to save macro
Press F4 to clear macro
Press ESC to exit
----------

waiting key
F1 - startStopMacro
F1 - startStopMacro
F2 - fireMacro
F3 - saveMacro
ESC - exitAutoHotKey
```







### Known bugs:

* the script crashes after saving a macro to a file and then trying to run the macro again. Workaround: restart the application after saving a macro to a file.



Copyright 2021 Ruslan Magana Vsevolodovna <contactATruslanmvDOTcom>
This program is distributed under the terms of the GNU Lesser General Public License.
