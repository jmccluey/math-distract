
#Math Distract

This is a project for PyEPL code that runs a math distraction task. Participants are given a fixed amount of time to solve as many math problems as they can. The code is generally used as part of a larger experiment. The project also has a program for just running math problems; this is intended for debugging purposes.

##Files

###math_distract.py

  This is the main module for running the distraction task. See distract_pres.py for an example of calling it. It is designed to use the same configuration variables as vcdMathMod.py, a previous version of this code. Unlike vcdMathMod.py, input of answers is not currently supported. Problems and proposed answers are shown, and participant must respond by pressing a button to indicate that the statement is "true" or "false".
  Detailed information about presentation timing is saved to a mathlog.

###distract_pres.py

  Code for presenting a set of math distraction periods. Can be used for debugging, and gives an example of calling math_distract.py.

###config_distract_pres.py###

  Config file for running distract_pres.py. Change this to alter the problems, timing, etc.

##Installation

[PyEPL](https://pyepl.sourceforge.net) is required, and the project must be on your path.

##Authors

Neal Morton wrote this project partially based on code from _vcdMathMod.py_ (written by unknown members of the [Kahana lab](http://memory.psych.upenn.edu), and other code by Josh McCluey.

