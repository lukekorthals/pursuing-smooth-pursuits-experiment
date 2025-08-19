# Programmer: Luke Korthals, https://github.com/lukekorthals/
# Initialize the eye tracker and run calibration without the experiment


# Libraries
from psychopy import visual, core, monitors

# Local imports
from classes.experiment.eyetracker import EyeTracker
from classes.utilities.settings import settings


mon = monitors.Monitor('myMonitor', width=settings["monitor"]["width"], distance=settings["monitor"]["distance"])
win = visual.Window(size=settings["monitor"]["resolution"], 
                                 fullscr=True, 
                                 monitor=mon, 
                                 units="pix", 
                                 color="black", 
                                 allowGUI=True)
et = EyeTracker(win, "Calibration","", dummy_mode=False)

et.connect_to_eyetracker()
et.prepare_calibration()
et.calibrate()
