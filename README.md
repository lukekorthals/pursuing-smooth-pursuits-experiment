# pursuing-smooth-pursuits-experiment
Experimental code used to collect data for the pursuing smooth pursuits research project. 

## Installation
1. Create virtual environment with Python 3.8
```bash
conda create -n psp-exp python=3.8
```
2. Install EyeLink Developers Kit from SR Research and install pylink 
3. Install wxPython
```bash
conda install conda-forge::wxpython
```
4. Install Psychopy without dependencies
```bash
pip install psychopy --no-deps
```
5. Install all other dependencies
```bash
pip install -r requirements.txt
```

## Stimulus Showcase
You can run the `stimulus_showcase.py` script to see how the different stimuli look. 

## Running the experiment
1. Set settings in `classes/utilities/settings.json`
    - **experiment:** Here you can enter information about the experiment, determine what trials to run (type, speed, trajectory, repetitions), and adjust the text for the tutorial.
    - **monitor:** Here you can set the size, resolution, refresh rate and distance of the monitor.
    - **tracker:** Here you can set tracker settings including sampling rate and calibration protocol. Set dummy_mode to `true` to run the experiment without an eye tracker.
    - **stimuli:** Here you can change the appearance of stimuli and text.
    - **controls:** Here you can set keys for starting, quitting, and recalibrating.
2. Run `run_experiment.py` to start the experiment.
3. Enter participant demographics
    - A dialog will appear where you can enter participant information.
    - Upon clicking "OK", a folder will be created for the participant in the `data` directory.
    - The folder contains a csv file with participant demographics and a csv file with the randomly generated trial order.
4. Calibrate the eyetracker 
    - The participant will be instructed to wait until calibration is complete.
    - Start calibration and validation of the eye tracker from the EyeLink computer.
5. Run tutorial trial
    - Instruct the participant to use the spacebar to control the experiment.
    - A tutorial trial will guide the participant through the process.
6. Ask the participant if they have any questions and tell them to proceed using the spacebar.
    - The participant will run through the trials as defined in the randomly generated trial order.
    - For each trial, the participant first fixates a target, presses the spacebar to remove the arrow indicating the target direction, presses the spacebar to start the trial, and then follows the target with their eyes without moving their head.
7. (If necessary) Recalibrate the eye tracker
    - If necessary, you can hit "c" (or the key defined in `settings.json`) to recalibrate the eye tracker in between trials.
8. After the last trial, the EDF file will be saved to the participant's folder and the experiment will end.
9. You can use the `create_asc_files.bat` script to convert EDF files to ASC files for further analysis.
10. You can use the `train_test_split.py` script to split participants into training and test sets for machine learning analysis.