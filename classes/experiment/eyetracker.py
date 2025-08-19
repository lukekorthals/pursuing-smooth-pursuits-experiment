# Programmer: Luke Korthals, https://github.com/lukekorthals/

# Classes and functions for communicating with the eye tracker

import pylink
from psychopy import core, visual
import sys

from classes.utilities.settings import settings
from classes.utilities.EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

class EyeTracker():
    def __init__(self, win: visual.Window, filename: str, data_path: str, dummy_mode=False):
        self.win = win
        self.filename = filename
        self.data_path = data_path
        self.dummy_mode = dummy_mode
    
    def connect_to_eyetracker(self) -> None:
        """Connects to the eyetracker PC"""
        if self.dummy_mode:
            self.el_tracker = pylink.EyeLink(None)
        else:
            try:
                self.el_tracker = pylink.EyeLink("100.1.1.1")
            except RuntimeError as error:
                print('ERROR:', error)
                core.quit()
                sys.exit()
    
    def open_edf_file(self) -> None:
        """Opens the edf file on host PC"""
        try:
            self.el_tracker.openDataFile(f"{self.filename}.EDF")
        except RuntimeError as err:
            print('ERROR:', err)
            # close the link if we have one open
            if self.el_tracker.isConnected():
                self.el_tracker.close()
            core.quit()
            sys.exit()
    
    def configure_eyetracker(self) -> None:
        # offline mode before changing parameters
        self.el_tracker.setOfflineMode()

        # Get version
        if self.dummy_mode:
            eyelink_ver = 0  # set version to 0, in case running in Dummy mode
        else:
            vstr = self.el_tracker.getTrackerVersionString()
            eyelink_ver = int(vstr.split()[-1].split('.')[0])

        # Events to save in the EDF file
        file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
        # Events to make available over the link
        link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
        # Sample data to be saved in EDF file
        if eyelink_ver > 3:
            file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
            link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
        else:
            file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
            link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'

        # Send commands
        self.el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
        self.el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
        self.el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
        self.el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

        # Sampling Rate to 1000hz
        if eyelink_ver > 2:
            self.el_tracker.sendCommand("sample_rate 1000")
        
        # Calibration type 
        self.el_tracker.sendCommand(f'calibration_type = {settings["tracker"]["calibration"]["calibration_type"]}')
    
    def prepare_calibration(self) -> None:
       """Sets up the graphics for calibration"""
       # Get screen resolution
       scn_width, scn_height = self.win.size
       # Pass pixel coordinates to tracker
       el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
       self.el_tracker.sendCommand(el_coords)
       # Add pixel coordinates to EDF file
       dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
       self.el_tracker.sendMessage(dv_coords)

       # Configure a graphics environment for calibration
       genv = EyeLinkCoreGraphicsPsychoPy(self.el_tracker, self.win)
       
       # Set calibration targets
       target_color = settings["tracker"]["calibration"]["target_color"]
       background_color = self.win.color
       genv.setCalibrationColors(target_color, background_color)
       genv.setTargetType(settings["tracker"]["calibration"]["target_type"])
       genv.setTargetSize(settings["tracker"]["calibration"]["target_size"])
       genv.setCalibrationSounds('off', 'off', 'off')

       # Tell pylink to use this graphics environment for calibration
       pylink.openGraphicsEx(genv)
    
    def calibrate(self) -> None:
        """Calibrates the eyetracker"""
        # calibrate eye tracker
        if not self.dummy_mode:
            try:
                self.el_tracker.doTrackerSetup()
            except RuntimeError as err:
                print('ERROR:', err)
                self.el_tracker.exitCalibration()
    
    def abort_trial(self) -> None:
        """Aborts the current trial"""
        # Stop recording
        if self.el_tracker.isRecording():
            # add 100 ms to catch final trial events
            pylink.pumpDelay(100)
            self.el_tracker.stopRecording()

        # Clear screen
        self.win.flip()

        # Clear data viewer message
        bgcolor_RGB = (116, 116, 116)
        self.el_tracker.sendMessage('!V CLEAR %d %d %d' % bgcolor_RGB)

        # End trial message
        self.el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_ERROR)
    
    def start_trial(self, trial_number: int) -> None:
        # Prepare tracker 
        self.el_tracker = pylink.getEYELINK()
        self.el_tracker.setOfflineMode()
        self.el_tracker.sendMessage('TRIALID %d' % trial_number)

        # Start recording
        try:
            self.el_tracker.startRecording(1, 1, 1, 1)
        except RuntimeError as error:
            print("ERROR:", error)
            self.abort_trial()
            print(pylink.TRIAL_ERROR)
        pylink.pumpDelay(100)

        # Onset message
        self.el_tracker.sendMessage(f'{trial_number}: TARGET_ONSET')

    def end_trial(self, trial_number: int) -> None:
        # Offset message 
        self.el_tracker.sendMessage(f'{trial_number}: TARGET_OFFSET')  
        # Stop recording
        pylink.pumpDelay(100)
        self.el_tracker.stopRecording()
        # End trial message
        self.el_tracker.sendMessage(f'{trial_number}: TRIAL_RESULT {pylink.TRIAL_OK}')

    def end_session(self) -> None:
        """ Terminate the task gracefully and retrieve the EDF data file

        file_to_retrieve: The EDF on the Host that we would like to download
        win: the current window used by the experimental script
        """
        if self.el_tracker.isConnected():
            # Terminate the current trial first if the task terminated prematurely
            error = self.el_tracker.isRecording()
            if error == pylink.TRIAL_OK:
                self.abort_trial()

            # Put tracker in Offline mode
            self.el_tracker.setOfflineMode()

            # Clear the Host PC screen and wait for 500 ms
            self.el_tracker.sendCommand('clear_screen 0')
            pylink.msecDelay(500)

            # Close the edf data file on the Host
            self.el_tracker.closeDataFile()

            # Download the EDF data file from the Host PC to a local data folder
            host_edf = f"{self.filename}.EDF"
            local_edf = f"{self.data_path}/{self.filename}.EDF"
            try:
                self.el_tracker.receiveDataFile(host_edf, local_edf)
            except RuntimeError as error:
                print('ERROR:', error)

            # Close the link to the tracker.
            self.el_tracker.close()

        # close the PsychoPy window
        self.win.close()

        # quit PsychoPy
        core.quit()
        sys.exit()
