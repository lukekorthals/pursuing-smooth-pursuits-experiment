# Programmer: Luke Korthals, https://github.com/lukekorthals/

# SPExperiment Class
# Experiment class for the current smooth pursuit experiment

# Libraries
from collections import OrderedDict
import csv
from datetime import datetime
import hashlib
import os
from psychopy import core, event, gui, visual, monitors
import random


# Local imports
from classes.experiment.experiment_section import ExperimentSection, SPTrialTutorial, SPTrialSection
from classes.experiment.eyetracker import EyeTracker
from classes.utilities.settings import settings


class Experiment:
    def __init__(self, 
                 name: str, # Name of the experiment
                 data_path: str, # Path to save data
                 settings: dict, # Settings dict should be a json file that includes all settings for the experiment
                 monitor_key: str = "monitor" # Key for the monitor settings in the settings dict
                 ): 
        self.name = name
        self.data_path = data_path
        self.settings = settings
        self.monitor_key = monitor_key
        self.data = OrderedDict(self.settings["experiment"]["data"].copy()) # Data should be a dict
        self.data["experiment_name"] = name
        self.experiment_clock = core.Clock()

    def setup_sections(self) -> None:
        """Sets the sections of the experiment"""
        raise NotImplementedError
        self.sections = [ExperimentSection(), # Add ExperimentSection objects to a list
                         ExperimentSection()] 
        
    def setup_filename(serlf):
        """Sets the filename for the current session"""
        raise NotImplementedError
        self.filename = "filename" # Should be string WITHOUT extension

    def create_data_file(self) -> None:
        """Creates a data file for the experiment"""
        with open(f"{self.data_path}/{self.filename}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.data.keys()) # Write column names to file
    
    def write_row_to_data_file(self, row: list) -> None:
        """Writes a row of data to the data file"""
        with open(f"{self.data_path}/{self.filename}.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(row)

    def prepare_experiment(self) -> None:
        """Functions that should be run before the main section loop"""
        self.setup_sections()
        self.setup_filename()
        self.create_data_file()
    
    def finalize_experiment(self) -> None:
        """Functions that should be run after the main section loop"""
        pass

    def run(self) -> None:
        """Prepares, runs, and finalizes the experiment"""
        # Prepare
        self.prepare_experiment()

        # Run
        print("########################")
        print("Runing through sections...")
        for section in self.sections:
            print(section.name)
            rows = section.run() # Run section and get data
            if rows is None:
                continue
            elif not isinstance(rows, list):
                raise Exception("Section must return a list or None")
            else:
                self.write_row_to_data_file(rows) # Write data to file

        # Finalize
        self.finalize_experiment() 


class SPExperiment(Experiment):
    def __init__(self, name = "sp_experiment", data_path="data", settings=settings, monitor_key="monitor"):
        super().__init__(name, data_path, settings, monitor_key)
        self.data["target_radius"] = settings["stimuli"]["targets"]["radius"]
        self.data["target_color"] = settings["stimuli"]["targets"]["fillColor"]
        self.participant_data = {}
        self.participant_data["experiment_name"] = name

    def generate_participant_id(self) -> None:
        """Generates a 8 character participant id from the current datetime"""
        sha256_hash = hashlib.sha256()
        time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sha256_hash.update(time.encode('utf-8'))
        hex_digest = sha256_hash.hexdigest()
        self.data["participant_id"] = hex_digest[:8]
        self.participant_data["participant_id"] = hex_digest[:8]
        
    def get_participant_info(self) -> None:
        # open gui to get participant info
        participant_info = {
                "Age": "",
                "Sex":["male", "female", "other", "prefer not to say"],
                "Eyecolor":["Brown", "Blue", "Gray", "Green", "Other"],
                "Eyecondition":["None", 
                                "Nearsighted, Glasses", 
                                "Nearsighted, Contacts", 
                                "Nearsighted, No Correction",
                                "Farsighted, Glasses", 
                                "Farsighted, Contacts", 
                                "Farsighted, No Correction"]
                                }
        participant_gui = gui.DlgFromDict(title="Participant Info", dictionary=participant_info, copyDict=True)
        participant_info = participant_gui.dictionary
        if participant_gui.OK:
            self.participant_data["participant_age"] = participant_info["Age"]
            self.participant_data["participant_sex"] = participant_info["Sex"]
            self.participant_data["participant_eyecolor"] = participant_info["Eyecolor"]
            self.participant_data["participant_eyecondition"] = participant_info["Eyecondition"]
        else:
            quit()
    
    def update_data_path(self) -> None:
        """Creates a new data path using the participant id"""
        if not os.path.exists(f"{self.data_path}/{self.data['participant_id']}"):
            os.makedirs(f"{self.data_path}/{self.data['participant_id']}")
        else:
            raise Exception("Participant ID already exists")
        self.data_path = f"{self.data_path}/{self.data['participant_id']}"

    def setup_filename(self) -> None:
        """Sets filename using participant id"""
        self.filename = self.data["participant_id"] # EDF file can only be 8 characters long -> participant id is 8 characters long

    def create_participant_data_file(self) -> None:
        """Writes participant info to a csv"""
        with open(f"{self.data_path}/{self.filename}_participant_info.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.participant_data.keys()) # Write column names to file
            writer.writerow(self.participant_data.values()) # Write column values to file

    def setup_window(self) -> None:
        mon = monitors.Monitor('myMonitor', width=settings[self.monitor_key]["width"], distance=settings[self.monitor_key]["distance"])
        self.win = visual.Window(size=settings[self.monitor_key]["resolution"], 
                                 fullscr=True, 
                                 monitor=mon, 
                                 units="pix", 
                                 color="black", 
                                 allowGUI=True)
    
    def setup_eyetracker(self) -> None:
        """Sets up the eyetracker"""
        # Initialize eyetracker
        self.el_tracker = EyeTracker(win=self.win, 
                                       filename=self.filename,
                                       data_path=self.data_path,
                                       dummy_mode=settings["tracker"]["settings"]["dummy_mode"])
        self.el_tracker.connect_to_eyetracker()
        self.el_tracker.open_edf_file()
        self.el_tracker.configure_eyetracker()

        # Calibrate eyetracker
        self.el_tracker.prepare_calibration()
        
        visual.TextStim(self.win, 
                        text=settings["tracker"]["calibration"]["instruction"], 
                        height=settings["stimuli"]["text"]["height"],
                        wrapWidth=settings["stimuli"]["text"]["wrapWidth"],
                        color=settings["stimuli"]["text"]["color"],
                        units=settings["stimuli"]["text"]["units"],
                        pos=settings["stimuli"]["text"]["pos"]).draw()
        self.win.flip()
        event.waitKeys(keyList=[settings["controls"]["continue"]])
        self.el_tracker.calibrate()

    def create_section_data_file(self) -> None:
        """Creates an overview of the sections in this session."""
        header = settings["experiment"]["section_data"]
        rows = []
        for section in self.sections:
            rows.append([self.name, self.data["participant_id"], section.name, section.data["trial_number"], section.data["target_type"], section.data["target_trajectory"], section.data["target_speed"], section.data["target_radius"], section.data["target_color"]])
        with open(f"{self.data_path}/{self.filename}_section_info.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

    def setup_sections(self) -> None:
        """Sets up all sections of the experiment"""
        target_types = settings["experiment"]["trials"]["target_types"]
        target_speeds = settings["experiment"]["trials"]["target_speeds"]
        target_trajectories = settings["experiment"]["trials"]["target_trajectories"]
        sections = []
        for i in range(settings["experiment"]["trials"]["repetitions"]):
            for speed in target_speeds:
                speed_section = []
                for target_trajectory in target_trajectories:
                    for target_type in target_types:
                        speed_section.append(SPTrialSection(name=None,
                                                        data=self.data.copy(),
                                                        win=self.win,
                                                        experiment_clock=self.experiment_clock,
                                                        el_tracker=self.el_tracker, 
                                                        trial_number=None, 
                                                        target_type=target_type, 
                                                        target_speed=speed, 
                                                        target_trajectory=target_trajectory))             
                random.shuffle(speed_section)
                sections += speed_section
        # Add Trial Name and Number
        i = 1
        for section in sections:
            if section.name == None:
                section.name = f"Trial {i}"
                section.data["trial_number"] = i
                i+=1
        self.sections = [SPTrialTutorial("Tutorial", 
                                         self.data.copy(), 
                                         self.experiment_clock, 
                                         self.win, self.el_tracker)] + sections

    def prepare_experiment(self) -> None:
        """Functions that should be run before the main section loop"""
        # Participant info
        print("Generating participant id...")
        self.generate_participant_id()
        print("Updating data path...")
        self.update_data_path()
        print("Setting up filename...")
        self.setup_filename()
        print("Getting participant info...")
        self.get_participant_info()
        # Data files
        print("Creating participant data file...")
        self.create_participant_data_file()
        print("Creating data file...")
        self.create_data_file()
        # Technical setup
        print("Setting up window...")
        self.setup_window()
        print("Setting up eyetracker...")        
        self.setup_eyetracker()
        print("Setting up sections...")
        self.setup_sections()
        print("Creating section data file...")
        self.create_section_data_file()
        
    
    def finalize_experiment(self) -> None:
        """Functions that should be run after the main section loop"""
        self.el_tracker.end_session()


class StimulusShowcase:
    def __init__(self, name="stimulus_showcase", data_path="data/showcase", settings=settings, monitor_key="monitor"):
        self.name = name
        self.data_path = data_path
        self.settings = settings
        self.monitor_key = monitor_key
        self.running = True
        self.data = settings["experiment"]["data"].copy()
        self.experiment_clock = core.Clock()

        self.setup_window()
        self.setup_eyetracker()
        self.setup_interface()

    def setup_window(self):
        mon = monitors.Monitor('myMonitor',
                               width=self.settings[self.monitor_key]["width"],
                               distance=self.settings[self.monitor_key]["distance"])
        self.win = visual.Window(
            size=self.settings[self.monitor_key]["resolution"],
            fullscr=False,
            pos = (0, 0),
            screen=0,
            allowGUI=False,
            units="pix",
            color="black"
        )
        self.win.flip()  # Prevents hanging on first flip

    def setup_eyetracker(self):
        os.makedirs(self.data_path, exist_ok=True)
        self.el_tracker = EyeTracker(
            win=self.win,
            filename="showcase",
            data_path=self.data_path,
            dummy_mode=self.settings["tracker"]["settings"]["dummy_mode"]
        )
        self.el_tracker.connect_to_eyetracker()
        self.el_tracker.open_edf_file()
        self.el_tracker.configure_eyetracker()
        self.el_tracker.prepare_calibration()

        visual.TextStim(
            self.win,
            text=self.settings["tracker"]["calibration"]["instruction"],
            height=self.settings["stimuli"]["text"]["height"],
            wrapWidth=self.settings["stimuli"]["text"]["wrapWidth"],
            color=self.settings["stimuli"]["text"]["color"],
            units=self.settings["stimuli"]["text"]["units"],
            pos=self.settings["stimuli"]["text"]["pos"]
        ).draw()
        self.win.flip()
        event.waitKeys(keyList=[self.settings["controls"]["continue"]])
        self.el_tracker.calibrate()

    def setup_interface(self):
        self.mouse = event.Mouse(visible=True, win=self.win)
        self.target_types = self.settings["experiment"]["trials"]["target_types"]
        self.target_trajectories = self.settings["experiment"]["trials"]["target_trajectories"]
        self.speed_options = self.settings["experiment"]["trials"]["target_speeds"]
        self.selected_type = self.target_types[0]
        self.selected_trajectory = self.target_trajectories[0]
        self.selected_speed = self.speed_options[0]
        self.tutorial_checked = False
        
        self.info_text = visual.TextStim(self.win, text=f"Click on 'Type', 'Speed', and 'Trajectory' to adjust them.\nCheck 'Tutorial' if you want to run it first.\nClick 'Run' to se the trial.", pos=(0, 250), height=24)
        self.speed_text = visual.TextStim(self.win, text=f"Speed: {self.selected_speed}", pos=(0, 100), height=24)
        self.type_text = visual.TextStim(self.win, text=f"Type: {self.selected_type}", pos=(-250, 100), height=24)
        self.traj_text = visual.TextStim(self.win, text=f"Trajectory: {self.selected_trajectory}", pos=(250, 100), height=24)
        self.checkbox_text = visual.TextStim(self.win, text="[ ] Tutorial", pos=(0, 50), height=24)

        self.buttons = {
            "run": self.make_button("Run", (0, -150)),
            "quit": self.make_button("Quit", (-150, -150))
        }

    def make_button(self, label, pos):
        return {
            "rect": visual.Rect(self.win, width=100, height=50, pos=pos, fillColor='gray'),
            "text": visual.TextStim(self.win, text=label, pos=pos, height=20)
        }

    def draw_interface(self):
        self.info_text.draw()
        self.speed_text.draw()
        self.type_text.draw()
        self.traj_text.draw()
        self.checkbox_text.draw()
        for b in self.buttons.values():
            b["rect"].draw()
            b["text"].draw()
        self.win.flip()

    def handle_interaction(self):
        if self.mouse.getPressed()[0]:
            mouse_pos = self.mouse.getPos()

            if self.checkbox_text.contains(mouse_pos):
                self.tutorial_checked = not self.tutorial_checked
                self.checkbox_text.text = "[x] Tutorial" if self.tutorial_checked else "[ ] Tutorial"
                core.wait(0.2)

            if self.type_text.contains(mouse_pos):
                i = self.target_types.index(self.selected_type)
                self.selected_type = self.target_types[(i + 1) % len(self.target_types)]
                self.type_text.text = f"Type: {self.selected_type}"
                core.wait(0.2)

            if self.traj_text.contains(mouse_pos):
                i = self.target_trajectories.index(self.selected_trajectory)
                self.selected_trajectory = self.target_trajectories[(i + 1) % len(self.target_trajectories)]
                self.traj_text.text = f"Trajectory: {self.selected_trajectory}"
                core.wait(0.2)
            
            if self.speed_text.contains(mouse_pos):
                i = self.speed_options.index(self.selected_speed)
                self.selected_speed = self.speed_options[(i + 1) % len(self.speed_options)]
                self.speed_text.text = f"Speed: {self.selected_speed}"
                core.wait(0.2)

            for name, button in self.buttons.items():
                if button["rect"].contains(mouse_pos):
                    core.wait(0.2)
                    return name
        return None

    def get_selection(self):
        return {
            "target_type": self.selected_type,
            "target_trajectory": self.selected_trajectory,
            "target_speed": self.selected_speed,
            "tutorial": self.tutorial_checked
        }

    def setup_sections(self, selection):
        sections = []
        if selection["tutorial"]:
            sections.append(SPTrialTutorial(
                name="Tutorial",
                data=self.data.copy(),
                experiment_clock=self.experiment_clock,
                win=self.win,
                el_tracker=self.el_tracker
            ))
        sections.append(SPTrialSection(
            name="Trial",
            data=self.data.copy(),
            win=self.win,
            experiment_clock=self.experiment_clock,
            el_tracker=self.el_tracker,
            trial_number=1,
            target_type=selection["target_type"],
            target_speed=selection["target_speed"],
            target_trajectory=selection["target_trajectory"]
        ))
        self.sections = sections

    def run(self):
        print("Stimulus Showcase started.")
        while self.running:
            self.draw_interface()
            action = self.handle_interaction()

            if action == "run":
                selection = self.get_selection()
                self.setup_sections(selection)
                for section in self.sections:
                    section.run()
            elif action == "quit":
                self.quit()
                break

    def quit(self):
        print("Exiting Stimulus Showcase.")
        self.running = False
        if hasattr(self, "el_tracker"):
            self.el_tracker.end_session()
        if hasattr(self, "win") and self.win:
            self.win.close()
        core.quit()
