import glob
import re
import pandas as pd
import pyreadr
from math import atan2, degrees

class Utilities:

    @staticmethod
    def px_to_deg(px, monitor):
    # px: the number of pixels to convert
    # monitor: the monitor settings
    # returns: the number of degrees
        return degrees(atan2(.5 * monitor["height"], monitor["distance"])) / (.5 * monitor["resolution"][1]) * px

    @staticmethod
    def deg_to_px(deg, monitor):
        # deg: the number of degrees to convert
        # monitor: the monitor settings
        # returns: the number of pixels
        return (deg / degrees(atan2(.5 * monitor["height"], monitor["distance"])) * (.5 * monitor["resolution"][1]))
    
    @staticmethod
    def match_trial_files(participant_ids=None, 
                          target_types=None, 
                          target_trajectories=None, 
                          target_speeds=None, 
                          trial="both",
                          excluded_participant_ids=None,
                          get_trial_numbers=False):
        if trial not in ["both", "first", "second"]:
            raise ValueError("trial has to be 'both', 'first', or 'second'")
        
        files = glob.glob("data/*/*/trials/*.csv")

        matching_files = []
        pattern_parts = []
        
        if participant_ids:
            pattern_parts.append(f'({"|".join(participant_ids)})')
            pattern_parts.append(f'({"|".join(participant_ids)})')
        else:
            pattern_parts.append('(.*)')
            pattern_parts.append('(.*)')
        
        if target_types:
            pattern_parts.append(f'({"|".join(target_types)})')
        else:
            pattern_parts.append('(.*)')
        
        if target_trajectories:
            pattern_parts.append(f'({"|".join(target_trajectories)})')
        else:
            pattern_parts.append('(.*)')
        
        if target_speeds:
            pattern_parts.append(f'({"|".join(target_speeds)})')
        else:
            pattern_parts.append('(.*)')
        
        pattern_parts.append('.csv')
        pattern = r'data\\(\w+)\\{}\\trials\\{}_(\d+)_{}_{}_{}.csv'.format(*pattern_parts)
        matching_files = [file for file in files if re.match(pattern, file)]

        if trial == "first":
            matching_files = [file for file in matching_files if int(re.match(r'data\\(\w+)\\{}\\trials\\{}_(\d+)_{}_{}_{}.csv'.format(*pattern_parts), file).group(3)) <= 72]
        elif trial == "second":
            matching_files = [file for file in matching_files if int(re.match(r'data\\(\w+)\\{}\\trials\\{}_(\d+)_{}_{}_{}.csv'.format(*pattern_parts), file).group(3)) > 72]

        if excluded_participant_ids:
            matching_files = [file for file in matching_files if re.match(r'data\\(\w+)\\{}\\trials\\{}_(\d+)_{}_{}_{}.csv'.format(*pattern_parts), file).group(2) not in excluded_participant_ids]
        
        if get_trial_numbers:
            # get the trial number which is the digit after the participant id
            trial_numbers = list(set([int(file.split("_")[1]) for file in matching_files]))
            trial_numbers.sort()
            return trial_numbers
        return matching_files

    @staticmethod
    def rename_to_readable_values(dat: pd.DataFrame):
        target_speed = {
            1: "1°/s", 
            3: "3°/s", 
            6: "6°/s"
            }
        target_type = {
            "moving_circle": "Moving Circle (SP)", 
            "jumping_circle": "Jumping Circle (FIX-SAC)", 
            "back_and_forth_array": "Back and Forth Circle (SP-SAC)"
            }
        target_trajectory = {
            "hor_right": "Horizontal Right →",
            "hor_left": "Horizontal Left ←",
            "ver_up": "Vertical Up ↑",
            "ver_down": "Vertical Down ↓",
            "diag_up_left": "Diagonal Up Left ↖",
            "diag_up_right": "Diagonal Up Right ↗",
            "diag_down_left": "Diagonal Down Left ↙",
            "diag_down_right": "Diagonal Down Right ↘"
        }
        dat.loc[:, "target_speed"] = dat["target_speed"].map(target_speed)
        dat.loc[:, "target_type"] = dat["target_type"].map(target_type)
        dat.loc[:, "target_trajectory"] = dat["target_trajectory"].map(target_trajectory)
        return dat
    
    @staticmethod
    def match_trial_files_by_trial_number(participant_ids=None, trial_numbers=None):
        "Matches trial files by participant id and trial number"
        files = glob.glob("data/*/*/trials/*.csv")
        matching_files = []
        pattern_parts = []

        if participant_ids:
                pattern_parts.append(f'({"|".join(participant_ids)})')
                pattern_parts.append(f'({"|".join(participant_ids)})')
        else:
            pattern_parts.append('(.*)')
            pattern_parts.append('(.*)')

        if trial_numbers: 
            pattern_parts.append(f'({"|".join(trial_numbers)})')
        else:
            pattern_parts.append('(.*)')

        pattern_parts.append('.csv')
        pattern = r'data\\(\w+)\\{}\\trials\\{}_{}_(.*).csv'.format(*pattern_parts)
        matching_files = [file for file in files if re.match(pattern, file)]
        return matching_files
    
    @staticmethod 
    def read_files(files):
        dat = pd.concat([pd.read_csv(file, dtype={"participant_id": str}) for file in files])
        return dat
    
    @staticmethod
    def read_gazehmm_files(participant_ids: list = None, trial_numbers: list = None):
        """Reads the RDS files according to the participant ids and trial numbers."""
        files = glob.glob("data/*/*/gazehmm/*.csv")
        matching_files = []
        pattern_parts = []

        if participant_ids:
                pattern_parts.append(f'({"|".join(participant_ids)})')
                pattern_parts.append(f'({"|".join(participant_ids)})')
        else:
            pattern_parts.append('(.*)')
            pattern_parts.append('(.*)')

        if trial_numbers: 
            pattern_parts.append(f'({"|".join(trial_numbers)})')
        else:
            pattern_parts.append('(.*)')

        pattern_parts.append('.rds')
        pattern = r'data\\(\w+)\\{}\\gazehmm\\{}_{}_gazehmm.csv'.format(*pattern_parts)
        matching_files = [file for file in files if re.match(pattern, file)]
        dat = pd.concat([pd.read_csv(file, dtype={"participant_id": str}) for file in matching_files])
        # rename time column to match the trial data
        dat = dat.rename(columns={"t": "trial_time"})
        # drop x and y columns
        dat = dat.drop(columns=["x", "y"])
        # change label values 
        dat.loc[:, "label"] = dat["label"].map({0: "Blink", 
                                                1: "Fixation", 
                                                2: "Saccade",
                                                3: "PSO",
                                                4: "Smooth Pursuit"})
        return dat
    
    @staticmethod
    def combine_trial_and_gazehmm_data(trial_data, gazehmm_data):
        """Merges the trial data and the gazehmm data."""
        dat = pd.merge(trial_data, gazehmm_data, on=["participant_id", "trial_number", "trial_time"])
        return dat



