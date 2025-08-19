# Programmer: Luke Korthals, https://github.com/lukekorthals/

# SPExperimentSection Class
# ExperimentSection classes for the current smooth pursuit experiment

# Libraries
from math import degrees, pi
from psychopy import core, event, visual 
from typing import List

# Local imports
from classes.experiment.eyetracker import EyeTracker
from classes.experiment.stimulus import JumpingCircle, MovingCircle, BackAndForthArray
from classes.experiment.trajectory import CircularTrajectory, HorizontalTrajectory, VerticalTrajectory, DiagonalTrajectory
from classes.utilities.settings import settings
from classes.utilities.utilities import Utilities

class ExperimentSection:
    def __init__(self, 
                 name: str, # Name of the section
                 data: dict,
                 experiment_clock: core.Clock) -> None: # Data should be inherited from the Experiment class
        self.name = name
        self.data = data
        self.experiment_clock = experiment_clock

    def run(self) -> dict:
        """Runs the section"""
        raise NotImplementedError
        return self.data # If data is supposed to be added to the csv, it should be returned here
    

class SPTextSection(ExperimentSection):
    def __init__(self, name: str, 
                 win: visual.Window,
                 text: str,
                 align = "center") -> None:
        super().__init__(name, data=None, experiment_clock=None)
        self.win = win
        self.text = text
        self.align = align
    
    def run(self):
        visual.TextStim(self.win, 
                        text=self.text, 
                        height=settings["stimuli"]["text"]["height"],
                        wrapWidth=settings["stimuli"]["text"]["wrapWidth"],
                        color=settings["stimuli"]["text"]["color"],
                        units=settings["stimuli"]["text"]["units"],
                        pos=(settings["stimuli"]["text"]["pos"][0], settings["stimuli"]["text"]["pos"][1]),
                        alignText=self.align).draw()
        self.win.flip()
        event.waitKeys(keyList=[settings["controls"]["continue"]])
        return None


class SPTrialSection(ExperimentSection):
    def __init__(self, 
                name: str,
                data: dict,
                experiment_clock: core.Clock,
                win: visual.Window,
                el_tracker: EyeTracker,
                trial_number: int,
                target_type: str,
                target_speed: float,
                target_trajectory: str,
                time_offset: int = 0) -> None:
    
        super().__init__(name, data, experiment_clock)
        self.win = win
        self.el_tracker = el_tracker
        self.data["section"] = name
        self.data["trial_number"] = trial_number
        self.data["target_type"] = target_type
        self.data["target_speed"] = target_speed
        self.data["target_trajectory"] = target_trajectory
        self.time_offset = time_offset
    
    def initialize_stimulus(self) -> None:
        """Initializes the stimulus"""
        # Speed, start position, required seconds
        speed_ang = self.data["target_speed"]
        speed_px = Utilities.deg_to_px(speed_ang, settings["monitor"])
        moving_distance = Utilities.deg_to_px(settings["stimuli"]["targets"]["moving_distance"], settings["monitor"])
        self.req_sec = moving_distance / speed_px
        if self.req_sec > settings["stimuli"]["targets"]["max_seconds"]:
            self.req_sec = settings["stimuli"]["targets"]["max_seconds"]
        speed = speed_px
        if "cir" in self.data["target_trajectory"]:
            circumference = 2 * pi * settings["monitor"]["distance"]
            distance_per_rotation_deg = degrees(circumference) / settings["monitor"]["distance"]
            time_per_rotation_sec = 360 / speed_ang
            self.req_sec = time_per_rotation_sec * (360 / distance_per_rotation_deg)
            speed = speed_ang
        # Trajectory
        if self.data["target_trajectory"] == "hor_right":
            start_pos = (-moving_distance/2, 0)
            trajectory = HorizontalTrajectory(moving_distance, "right")
        elif self.data["target_trajectory"] == "hor_left":
            start_pos = (moving_distance/2, 0)
            trajectory = HorizontalTrajectory(moving_distance, "left")
        elif self.data["target_trajectory"] == "ver_up":
            start_pos = (0, -moving_distance/2)
            trajectory = VerticalTrajectory(moving_distance, "up")
        elif self.data["target_trajectory"] == "ver_down":
            start_pos = (0, moving_distance/2)
            trajectory = VerticalTrajectory(moving_distance, "down")
        elif self.data["target_trajectory"] == "diag_up_right":
            start_pos = (-moving_distance/2, -moving_distance/2)
            trajectory = DiagonalTrajectory(moving_distance, "up_right")
        elif self.data["target_trajectory"] == "diag_up_left":
            start_pos = (moving_distance/2, -moving_distance/2)
            trajectory = DiagonalTrajectory(moving_distance, "up_left")
        elif self.data["target_trajectory"] == "diag_down_right":
            start_pos = (-moving_distance/2, moving_distance/2)
            trajectory = DiagonalTrajectory(moving_distance, "down_right")
        elif self.data["target_trajectory"] == "diag_down_left":
            start_pos = (moving_distance/2, moving_distance/2)
            trajectory = DiagonalTrajectory(moving_distance, "down_left")
        elif self.data["target_trajectory"] == "cir_clock":
            start_pos = (-moving_distance/2, 0)
            trajectory = CircularTrajectory(radius=moving_distance/2, direction="clockwise", start=0, monitor=settings["monitor"])
        elif self.data["target_trajectory"] == "cir_counter":
            start_pos = (moving_distance/2, 0)
            trajectory = CircularTrajectory(radius=moving_distance/2, direction="counterclockwise", start=0, monitor=settings["monitor"])
        # Stimulus
        radius = settings["stimuli"]["targets"]["radius"]
        fill_color = settings["stimuli"]["targets"]["fillColor"]
        line_color = settings["stimuli"]["targets"]["lineColor"]
        if self.data["target_type"] == "moving_circle":
            self.stimulus = MovingCircle(win=self.win, 
                                         pos=start_pos, 
                                         speed=speed, 
                                         trajectory=trajectory, 
                                         radius=radius, 
                                         fill_color=fill_color,
                                         line_color=line_color)
        elif self.data["target_type"] == "jumping_circle":
            jumping_frequency = round(settings["monitor"]["refresh_rate"] / settings["stimuli"]["targets"]["jumps_per_second"]) 
            self.stimulus = JumpingCircle(win=self.win, 
                                          pos=start_pos, 
                                          speed=speed, 
                                          trajectory=trajectory, 
                                          update_frequency=jumping_frequency,
                                          radius=radius,
                                          fill_color=fill_color,
                                          line_color=line_color)
        elif self.data["target_type"] == "back_and_forth_array":
            jumping_frequency = round(settings["monitor"]["refresh_rate"] / settings["stimuli"]["targets"]["jumps_per_second"])
            self.stimulus = BackAndForthArray(win=self.win,
                                              pos=start_pos,
                                              speed=speed,
                                              trajectory=trajectory,
                                              update_frequency=jumping_frequency,
                                              radius=radius,
                                              element_sizes=2*radius, # double the radius to make the elements the same size as the other targets
                                              element_colors=fill_color)
            
    def draw_instruction_arrow(self, start_pos, length, trajectory, color="white", line_width=2):
        valid_trajectories = ["hor_right", "hor_left", "ver_up", "ver_down", "diag_up_right", "diag_up_left", "diag_down_right", "diag_down_left"]
        if trajectory not in valid_trajectories:
            raise ValueError(f"Invalid trajectory ({trajectory})")
        tip_length = 0.3*length
        tip_width = 0.1*length
        if trajectory == "hor_right":
            end_pos = (start_pos[0] + length, start_pos[1])
            tip_vertices = [(end_pos[0] - tip_length, end_pos[1] + tip_width), end_pos, (end_pos[0] - tip_length, end_pos[1] - tip_width)]
        elif trajectory == "hor_left":
            end_pos = (start_pos[0] - length, start_pos[1])
            tip_vertices = [(end_pos[0] + tip_length, end_pos[1] + tip_width), end_pos, (end_pos[0] + tip_length, end_pos[1] - tip_width)]
        elif trajectory == "ver_up":
            end_pos = (start_pos[0], start_pos[1] + length)
            tip_vertices = [(end_pos[0] - tip_width, end_pos[1] - tip_length), end_pos, (end_pos[0] + tip_width, end_pos[1] - tip_length)]
        elif trajectory == "ver_down":
            end_pos = (start_pos[0], start_pos[1] - length)
            tip_vertices = [(end_pos[0] - tip_width, end_pos[1] + tip_length), end_pos, (end_pos[0] + tip_width, end_pos[1] + tip_length)]
        elif trajectory == "diag_up_right":
            end_pos = (start_pos[0] + length, start_pos[1] + length)
            tip_vertices = [(end_pos[0] - tip_length, end_pos[1] - tip_width), end_pos, (end_pos[0] - tip_width, end_pos[1] - tip_length)]
        elif trajectory == "diag_up_left":
            end_pos = (start_pos[0] - length, start_pos[1] + length)
            tip_vertices = [(end_pos[0] + tip_length, end_pos[1] - tip_width), end_pos, (end_pos[0] + tip_width, end_pos[1] - tip_length)]
        elif trajectory == "diag_down_right":
            end_pos = (start_pos[0] + length, start_pos[1] - length)
            tip_vertices = [(end_pos[0] - tip_length, end_pos[1] + tip_width), end_pos, (end_pos[0] - tip_width, end_pos[1] + tip_length)]
        elif trajectory == "diag_down_left":
            end_pos = (start_pos[0] - length, start_pos[1] - length)
            tip_vertices = [(end_pos[0] + tip_length, end_pos[1] + tip_width), end_pos, (end_pos[0] + tip_width, end_pos[1] + tip_length)]
        line_vertices = [start_pos, end_pos]
        visual.ShapeStim(self.win, vertices=line_vertices+tip_vertices, lineColor=color, lineWidth=line_width, closeShape=False).draw()
    
    def draw_instruction_text(self, movement_text: str, trajectory_text: str) -> None:
        instruction_text = f"Fixate on the target as it {movement_text} {trajectory_text}.\n\nFixate the target, press {settings['controls']['continue']} to make the text disappear, and press {settings['controls']['continue']} again to start the trial."
        visual.TextStim(
            self.win, 
            text=instruction_text, 
            height=settings["stimuli"]["text"]["height"],
            wrapWidth=settings["stimuli"]["text"]["wrapWidth"],
            color=settings["stimuli"]["text"]["color"],
            units=settings["stimuli"]["text"]["units"],
            pos=(settings["stimuli"]["text"]["pos"][0], settings["stimuli"]["text"]["pos"][1])
            ).draw()
        
    def get_instruction_settings(self):
        # Offset and trajectory text
        offset = 50
        x_offset = 0
        y_offset = 0
        if self.data["target_trajectory"] == "hor_right":
            trajectory_text = "horizontally to the right"
            x_offset = offset
        elif self.data["target_trajectory"] == "hor_left":
            trajectory_text = "horizontally to the left"
            x_offset = -offset
        elif self.data["target_trajectory"] == "ver_up":
            trajectory_text = "vertically upwards"
            y_offset = offset
        elif self.data["target_trajectory"] == "ver_down":
            trajectory_text = "vertically downwards"
            y_offset = -offset
        elif self.data["target_trajectory"] == "diag_up_right":
            trajectory_text = "diagonally upwards to the right"
            x_offset = offset
            y_offset = offset
        elif self.data["target_trajectory"] == "diag_up_left":
            trajectory_text = "diagonally upwards to the left"
            x_offset = -offset
            y_offset = offset
        elif self.data["target_trajectory"] == "diag_down_right":
            trajectory_text = "diagonally downwards to the right"
            x_offset = offset
            y_offset = -offset
        elif self.data["target_trajectory"] == "diag_down_left":
            trajectory_text = "diagonally downwards to the left"
            x_offset = -offset
            y_offset = -offset
        elif self.data["target_trajectory"] == "cir_clock":
            trajectory_text = "in a clockwise circle"
        elif self.data["target_trajectory"] == "cir_counter":
            trajectory_text = "in a counterclockwise circle"

        # Movement text
        if self.data["target_type"] == "moving_circle":
            movement_text = "moves consistently"
        elif self.data["target_type"] == "jumping_circle":
            movement_text = "jumps"
        elif self.data["target_type"] == "back_and_forth_array":
            movement_text = "jumps back and forth, while moving"
        return x_offset, y_offset, trajectory_text, movement_text
    
    def draw_instruction_target(self):
        params = {"current_time": self.time_offset, "current_frame": 0, "final_update": False}        
        self.stimulus.update(params)
        self.stimulus.target.draw()
    
    def draw_arrow_and_target(self):
        # Get instruction settings
        x_offset, y_offset, trajectory_text, movement_text = self.get_instruction_settings()
        
        # Draw trajectory arrow
        arrow_start_pos = (self.stimulus.pos[0] + x_offset, self.stimulus.pos[1] + y_offset)
        self.draw_instruction_arrow(start_pos=arrow_start_pos, length=100, trajectory=self.data["target_trajectory"], line_width=5) 
        
        # Draw target
        self.draw_instruction_target()

        # Flip window
        self.win.flip()

    
    def check_recalibrate(self):
        ready = True
        keys = event.waitKeys(keyList=[settings["controls"]["continue"], settings["controls"]["recalibrate"]])
        if settings["controls"]["recalibrate"] in keys:
            print("Recalibrating...")
            self.win.flip()   
            self.el_tracker.calibrate()
            ready = False
        return ready

    def remove_direction_arrow(self):
        event.waitKeys(keyList=[settings["controls"]["continue"]])
        self.stimulus.target.draw()
        self.win.flip()
    
    def start_trial(self):
        event.waitKeys(keyList=[settings["controls"]["continue"]])

    def fixation_instruction(self) -> None:
        """Draws the target and asks the participant to fixate on it"""        
        ready = False
        while not ready:
            # Draw arrow and target
            self.draw_arrow_and_target()
            
            # Check recalibrate
            ready = self.check_recalibrate()

        # Remove direction arrow
        self.draw_instruction_target()
        self.win.flip()


        # Start trial
        self.start_trial()

    def move_target(self, extra_draws: visual.BaseVisualStim = []) -> List[list]:
        rows = []
        frame = 0
        
        # Start EyeLink recording
        self.el_tracker.start_trial(self.data["trial_number"])
        
        # Move the target
        trial_clock = core.Clock()
        while trial_clock.getTime() < self.req_sec:
            # Update target position
            frame += 1
            params = {"current_time": trial_clock.getTime() + self.time_offset, "current_frame": frame, "final_update": False}           
            target_position = self.stimulus.update(params)
            self.stimulus.target.draw()
            for extra_draw in extra_draws:
                extra_draw.draw()
            self.win.flip()

            # Save data
            self.data["experiment_time"] = self.experiment_clock.getTime()
            self.data["trial_time"] = trial_clock.getTime()
            self.data["target_x"] = target_position[0]
            self.data["target_y"] = target_position[1]
            rows.append([value for value in self.data.values()])
    
            # Check cancelation
            if settings["controls"]["quit"] in event.getKeys():
                self.el_tracker.end_session()
            event.clearEvents()

        # One final update to end jumping stimuli at the final position
        params = {"current_time": trial_clock.getTime() + self.time_offset, "current_frame": frame, "final_update": True}           
        target_position = self.stimulus.update(params)
        self.stimulus.target.draw()
        self.win.flip()
        core.wait(0.2) # wait 200ms on final fixation
        # Stop EyeLink recording
        self.el_tracker.end_trial(self.data["trial_number"])
        return rows

    def run(self):
        # Initialize stimulus
        self.initialize_stimulus()
        
        # Show instructions
        self.fixation_instruction()
        
        # Move target
        rows = self.move_target()
        return rows

class SPTrialTutorial(SPTrialSection):
    def __init__(self, 
                name: str,
                data: dict,
                experiment_clock: core.Clock,
                win: visual.Window,
                el_tracker: EyeTracker,
                trial_number: int = 0,
                target_type: str = "moving_circle",
                target_speed: float = 1,
                target_trajectory: str = "hor_right",
                time_offset: int = 0) -> None:
        super().__init__(name, data, experiment_clock, win, el_tracker, trial_number, target_type, target_speed, target_trajectory, time_offset)
        self.data["target_speed"] = 2
    
    def tutorial_step_1(self):
        """Draw target"""
        # Draw target
        self.draw_instruction_target()

        # Draw step 1 instruction text
        visual.TextStim(
            self.win, 
            text=settings["experiment"]["tutorial"]["step_1"], 
            height=0.05,
            wrapWidth=0.5,
            color=settings["stimuli"]["text"]["color"],
            units="norm",
            pos=(0, 0.5)
            ).draw()
        
        # Flip window
        self.win.flip()

        # Wait for continue key
        event.waitKeys(keyList=[settings["controls"]["continue"]])

    def tutorial_step_2(self):
        """Draw arrow"""
        # Draw target
        self.draw_instruction_target()

        # Get instruction settings
        x_offset, y_offset, trajectory_text, movement_text = self.get_instruction_settings()

        # Draw arrow
        arrow_start_pos = (self.stimulus.pos[0] + x_offset, self.stimulus.pos[1] + y_offset)
        self.draw_instruction_arrow(start_pos=arrow_start_pos, length=100, trajectory=self.data["target_trajectory"], line_width=5)
       
       # Draw step 2 instruction text
        visual.TextStim(
            self.win,
            text=settings["experiment"]["tutorial"]["step_2"],
            height=0.05,
            wrapWidth=0.5,
            color=settings["stimuli"]["text"]["color"],
            units="norm",
            pos=(0, 0.5)
            ).draw()
        
        # Flip window
        self.win.flip()

        # Wait for continue key
        event.waitKeys(keyList=[settings["controls"]["continue"]])

    def tutorial_step_3(self):
        """Remove arrow"""
        # Draw target
        self.draw_instruction_target()

        # Get instruction settings
        x_offset, y_offset, trajectory_text, movement_text = self.get_instruction_settings()

        # Draw arrow
        arrow_start_pos = (self.stimulus.pos[0] + x_offset, self.stimulus.pos[1] + y_offset)
        self.draw_instruction_arrow(start_pos=arrow_start_pos, length=100, trajectory=self.data["target_trajectory"], line_width=5)

        # Draw step 3 instruction text
        visual.TextStim(
            self.win,
            text=settings["experiment"]["tutorial"]["step_3"],
            height=0.05,
            wrapWidth=0.5,
            color=settings["stimuli"]["text"]["color"],
            units="norm",
            pos=(0, 0.5)
            ).draw()
        
        # Flip window
        self.win.flip()

        # Remove direction arrow
        self.remove_direction_arrow()
    
    def tutorial_step_4(self):
        """Start trial"""
        # Draw target
        self.draw_instruction_target()

        # Draw step 4 instruction text
        visual.TextStim(
            self.win,
            text=settings["experiment"]["tutorial"]["step_4"],
            height=0.05,
            wrapWidth=0.5,
            color=settings["stimuli"]["text"]["color"],
            units="norm",
            pos=(0, 0.5)
            ).draw()
        
        # Flip window
        self.win.flip()

        # Start trial
        self.start_trial()

    def tutorial_step_5(self):
        # Draw step 5 instruction text
        rows = self.move_target(extra_draws=[
            visual.TextStim(
            self.win,
            text=settings["experiment"]["tutorial"]["step_5"],
            height=0.05,
            wrapWidth=0.5,
            color=settings["stimuli"]["text"]["color"],
            units="norm",
            pos=(0, 0.5)
            )
        ])  
        return rows
    
    def tutorial_step_6(self):        
        # Draw target
        self.draw_instruction_target()

        # Get instruction settings
        x_offset, y_offset, trajectory_text, movement_text = self.get_instruction_settings()

        # Draw arrow
        arrow_start_pos = (self.stimulus.pos[0] + x_offset, self.stimulus.pos[1] + y_offset)
        self.draw_instruction_arrow(start_pos=arrow_start_pos, length=100, trajectory=self.data["target_trajectory"], line_width=5)

        # Draw step 6 instruction text
        visual.TextStim(
            self.win,
            text=settings["experiment"]["tutorial"]["step_6"],
            height=settings["stimuli"]["text"]["height"],
            wrapWidth=settings["stimuli"]["text"]["wrapWidth"],
            color=settings["stimuli"]["text"]["color"],
            units=settings["stimuli"]["text"]["units"],
            pos=settings["stimuli"]["text"]["pos"]
            ).draw()

        # Flip window
        self.win.flip()

        # Wait for continue key
        event.waitKeys(keyList=[settings["controls"]["continue"]])

    def run(self):
        self.initialize_stimulus()
        self.tutorial_step_1()
        self.tutorial_step_2()
        self.tutorial_step_3()
        self.tutorial_step_4()
        rows = self.tutorial_step_5()
        self.tutorial_step_6()
        return rows

