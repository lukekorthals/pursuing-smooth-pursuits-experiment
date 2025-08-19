# Stimuli are targets shown on a psychopy window and that are updated every frame
from math import cos, sin, radians, degrees, atan2, pi
from numpy.random import choice
from psychopy import visual
from typing import Tuple, List

from classes.experiment.trajectory import Trajectory, HorizontalTrajectory, VerticalTrajectory, CircularTrajectory, DiagonalTrajectory

class Stimulus:
    """Basic stimulus class serves as a template"""
    def __init__(self, 
                 win: visual.Window, 
                 pos: Tuple[float, float]) -> None:
        if not isinstance(win, visual.Window):
            raise ValueError("window must be an instance of psychopy.visual.Window")
        if not isinstance(pos, tuple):
            raise ValueError("pos must be a tuple")
        if not len(pos) == 2:
            raise ValueError("pos must be a tuple of length 2")
        if not isinstance(pos[0], int) and not isinstance(pos[0], float) and not isinstance(pos[1], int) and not isinstance(pos[1], float):
            raise ValueError("pos[0] must be an int or a float")
        self.window = win
        self.pos = pos

    def update(self, params: dict) -> Tuple[float]:
        """Overwritten by subclasses with moving stimuli.
        Must return self.target.pos"""
        if not isinstance(params, dict):
            raise ValueError("params must be a dict")
        pass


class CircleStimulus(Stimulus):
    """A circle that does not move"""
    def __init__(self, 
                 win: visual.Window, 
                 pos: Tuple[float, float], 
                 radius = 30, 
                 fill_color = "white", 
                 line_color = "white") -> None:
        super().__init__(win, pos)
        if not isinstance(radius, int) and not isinstance(radius, float):
            raise ValueError("radius must be an int or float")
        self.target = visual.Circle(self.window, radius = radius, fillColor = fill_color, lineColor = line_color, pos = self.pos)


class MovingCircle(CircleStimulus):
    """A circle moving along a trajectory"""
    def __init__(self, 
                 win: visual.Window, 
                 pos: Tuple[float, float], 
                 radius = 30, 
                 fill_color = "white", 
                 line_color = "white", 
                 speed = 1, 
                 trajectory: Trajectory = None) -> None:
        super().__init__(win, pos, radius, fill_color, line_color)
        if not isinstance(speed, float) and not isinstance(speed, int):
            raise ValueError("speed must be a int or float")
        if not isinstance(trajectory, Trajectory):
            raise ValueError("trajectory must be an instance of Trajectory")
        self.speed = speed
        self.trajectory = trajectory

    def update(self, params: dict) -> None:
        """Updates the position of the stimulus"""
        super().update(params)
        current_time = params["current_time"]
        self.target.pos = self.trajectory.update_position(self.target.pos, current_time, self.speed)
        self.target.ori = self.trajectory.update_orientation(self.target.pos, current_time, self.speed)
        return self.target.pos


class JumpingCircle(MovingCircle):
    """A circle that appears stationary at different positions along a trajectory"""
    def __init__(self, 
                 win: visual.Window, 
                 pos: Tuple[float, float], 
                 radius = 30, 
                 fill_color = "white", 
                 line_color = "white", 
                 speed = 1, 
                 trajectory: Trajectory = None,
                 update_frequency = None) -> None: # defines how many frames the position of the circle should be updated, None means never
        super().__init__(win, pos, radius, fill_color, line_color, speed, trajectory)
        self.update_frequency = update_frequency
    
    def update(self, params: dict) -> None:
        """Updates the position of the stimulus"""
        if not self.update_frequency is None:
            current_frame = params["current_frame"]
            final_update = params["final_update"]
            if current_frame % self.update_frequency == 0 or current_frame == 1 or final_update:
                super().update(params)
        return self.target.pos


class LineStimulus(Stimulus):
    """A line that does not move"""
    def __init__(self, 
                 win: visual.Window, 
                 start: Tuple[float, float], 
                 end: Tuple[float, float], 
                 line_width = 1, 
                 line_color = "white") -> None:
        super().__init__(win)
        if not isinstance(start, tuple) or not isinstance(end, tuple):
            raise ValueError("start and end must be tuples")
        if not len(start) == 2 or not len(end) == 2:
            raise ValueError("start and end must be tuples of length 2")
        if not isinstance(start[0], int) and not isinstance(start[0], float) and not isinstance(start[1], int) and not isinstance(start[1], float):
            raise ValueError("start[0] and start[1] must be ints or floats")
        if not isinstance(end[0], int) and not isinstance(end[0], float) and not isinstance(end[1], int) and not isinstance(end[1], float):
            raise ValueError("end[0] and end[1] must be ints or floats")
        if not isinstance(line_width, int) and not isinstance(line_width, float):
            raise ValueError("width must be an int or float")
        self.target = visual.Line(self.window, start = start, end = end, lineWidth = line_width, lineColor = line_color)

class ArrayStimulus(Stimulus):
    """An array of circles that does not move"""
    def __init__(self, 
                 win: visual.Window, 
                 pos: Tuple[float, float], 
                 radius = 30,
                 n_elements = 100,
                 element_colors = "white", 
                 element_sizes = 10,
                 element_xys: List[Tuple[float]] = None) -> None:
        super().__init__(win, pos)
        self.target = visual.ElementArrayStim(self.window, 
                                              nElements = n_elements, 
                                              fieldPos = pos, 
                                              fieldSize = radius*2, 
                                              fieldShape = "circle", 
                                              sizes = element_sizes, 
                                              colors = element_colors,
                                              xys = element_xys, 
                                              elementMask = "circle", 
                                              elementTex = None)

class BackAndForthArray(ArrayStimulus):
    """An array of circles moving along a trajectory"""
    def __init__(self, 
                 win: visual.Window, 
                 pos: Tuple[float, float], 
                 radius = 20,
                 element_colors = "white", 
                 element_sizes = 100,
                 speed = 1, 
                 trajectory: Trajectory = None,
                 update_frequency = None) -> None:
        super().__init__(win=win, 
                         pos=pos, 
                         radius=radius, 
                         n_elements=1, 
                         element_colors=element_colors, 
                         element_sizes=element_sizes, 
                         element_xys=[(0, 0)])
        if not isinstance(speed, float) and not isinstance(speed, int):
            raise ValueError("speed must be a int or float")
        if not isinstance(trajectory, Trajectory):
            raise ValueError("trajectory must be an instance of Trajectory")
        self.speed = speed
        self.trajectory = trajectory
        self.update_frequency = update_frequency
        self.back = True

    def update_xys(self) -> None:
        """Updates the position of the target in the array to match the current movement vector"""
        if isinstance(self.trajectory, HorizontalTrajectory):
            back = [(-self.target.fieldSize[0], 0)]
            forth = [(self.target.fieldSize[0], 0)]
        elif isinstance(self.trajectory, VerticalTrajectory):
            back = [(0, -self.target.fieldSize[1])]
            forth = [(0, self.target.fieldSize[1])]
        elif isinstance(self.trajectory, DiagonalTrajectory):
            if self.trajectory.direction == "up_right":
                back = [(-self.target.fieldSize[0], -self.target.fieldSize[1])]
                forth = [(self.target.fieldSize[0], self.target.fieldSize[1])]
            elif self.trajectory.direction == "up_left":
                back = [(self.target.fieldSize[0], -self.target.fieldSize[1])]
                forth = [(-self.target.fieldSize[0], self.target.fieldSize[1])]
            elif self.trajectory.direction == "down_right":
                back = [(-self.target.fieldSize[0], self.target.fieldSize[1])]
                forth = [(self.target.fieldSize[0], -self.target.fieldSize[1])]
            elif self.trajectory.direction == "down_left":
                back = [(self.target.fieldSize[0], self.target.fieldSize[1])]
                forth = [(-self.target.fieldSize[0], -self.target.fieldSize[1])]
        
        elif isinstance(self.trajectory, CircularTrajectory):
            # tangent along the current point on the radius of the circle with center (0,0)
            current_pos = self.target.fieldPos
            center = (0,0)
            # calculate degrees from x and y
            deg = degrees(atan2(current_pos[1] - center[1], current_pos[0] - center[0]))

            # Calculate the coordinates of the tangent line endpoints
            tangent_angle = deg + 90
            tangent_start_x = -self.target.fieldSize[0] * cos(radians(tangent_angle))
            tangent_start_y = -self.target.fieldSize[1] * sin(radians(tangent_angle))
            tangent_end_x = self.target.fieldSize[0] * cos(radians(tangent_angle))
            tangent_end_y = -self.target.fieldSize[1] * sin(radians(tangent_angle))
            back = [(tangent_start_x, tangent_start_y)]
            forth = [(tangent_end_x, tangent_end_y)]
        if self.back:
            self.target.xys = back
            self.back = False
        else:
            self.target.xys = forth
            self.back = True

    def update(self, params: dict) -> None:
        """Updates the position of the stimulus"""
        super().update(params)
        current_time = params["current_time"]
        self.target.fieldPos = self.trajectory.update_position(self.target.fieldPos, current_time, self.speed)
        if not self.update_frequency is None:
            current_frame = params["current_frame"]
            if current_frame % self.update_frequency == 0 or current_frame == 1:
                self.update_xys()
        x = self.target.fieldPos[0] - self.target.xys[0][0] 
        y = self.target.fieldPos[1] - self.target.xys[0][1] 
        return (x, y)


class SwarmStimulus(Stimulus):
    """A collection of small circles arranged in a circular grid that does not move"""
    def __init__(self, 
                 win: visual.Window, 
                 pos: Tuple[float, float], # defines position of the field center
                 radius = 30, 
                 n_elements = 100, # number of elements placed at random positions within the field
                 n_active = 10, # number of elements that should be visible
                 element_sizes = 10,
                 element_colors = "white",
                 update_frequency = None) -> None: # defines how many frames the position of active elements should be updated, None means never
        super().__init__(win, pos)
        if not isinstance(radius, int) and not isinstance(radius, float):
            raise ValueError("radius must be an int or float")
        if not isinstance(n_elements, int):
            raise ValueError("n must be an int")
        if not isinstance(n_active, int):
            raise ValueError("n_active must be an int")
        if not isinstance(element_sizes, int) and not isinstance(element_sizes, float) and not isinstance(element_sizes, list):
            raise ValueError("element_sizes must be an int, float, or list of length n_elements of ints or floats")
        if isinstance(element_sizes, list) and not len(element_sizes) == n_elements:
            raise ValueError("element_sizes must be a list of length n_elements")
        if isinstance(element_sizes, list) and not all([isinstance(x, int) or isinstance(x, float) for x in element_sizes]):
            raise ValueError("element_sizes must be a list of ints or floats")
        if not isinstance(element_colors, str) and not isinstance(element_colors, list):
            raise ValueError("element_colors must be a string or a list of length n_elements of strings")
        if isinstance(element_colors, list) and not len(element_colors) == n_elements:
            raise ValueError("element_colors must be a list of length n_elements")
        if isinstance(element_colors, list) and not all([isinstance(x, str) for x in element_colors]):
            raise ValueError("element_colors must be a list of strings")
        if not isinstance(update_frequency, int) and not update_frequency is None:
            raise ValueError("update_frequency must be an int")
        self.n = n_elements
        self.n_active = n_active
        self.update_frequency = update_frequency
        self.target = visual.ElementArrayStim(self.window, nElements = self.n, fieldPos = pos, fieldSize = radius*2, fieldShape = "circle", sizes = element_sizes, colors = element_colors, elementMask = "circle", elementTex = None)
        self.target.opacities = 0
        for i in range(self.n_active): # turn on n_active elements
            j = choice(range(self.n), replace = False)
            self.target.opacities[j] = 1
        
    def update(self, params: dict) -> None:
        """Updates the position of the active elements"""
        super().update(params)
        if not self.update_frequency is None:
            current_frame = params["current_frame"]
            if current_frame % self.update_frequency == 0:
                self.target.opacities = 0
                for i in range(self.n_active):
                    j = choice(range(self.n), replace = False)
                    self.target.opacities[j] = 1


class MovingSwarm(SwarmStimulus):
    def __init__(self, 
                 win: visual.Window, 
                 pos: Tuple[float, float], 
                 radius=30, 
                 n_elements=100, 
                 n_active=10, 
                 element_sizes=10, 
                 element_colors="white", 
                 update_frequency=None,
                 speed = 1, 
                 trajectory: Trajectory = None) -> None:
        super().__init__(win, pos, radius, n_elements, n_active, element_sizes, element_colors, update_frequency)
        if not isinstance(speed, float) and not isinstance(speed, int):
            raise ValueError("speed must be a int or float")
        if not isinstance(trajectory, Trajectory):
            raise ValueError("trajectory must be an instance of Trajectory")
        self.speed = speed
        self.trajectory = trajectory

    def update(self, params: dict) -> None:
        """Updates the position of the active elements and moves the field along the trajectory"""
        super().update(params)
        current_time = params["current_time"]
        self.target.fieldPos = self.trajectory.update_position(self.target.fieldPos, current_time, self.speed)
        return self.target.fieldPos


