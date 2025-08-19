# Trajectories are mathematical functions that describe how a target moves accross the screen
# They can update the target position according to their function, the current target position, the speed of the target, and the time step
from typing import Tuple
from math import cos, sin, radians, degrees, atan2, pi
from classes.utilities.utilities import Utilities

class Trajectory:
    def update_position(self, current_position: Tuple[float, float], time_step: float, speed: float) -> Tuple[float, float]:
        """This method should be overridden by subclasses"""
        raise NotImplementedError
    
    def update_orientation(self, current_position: Tuple[float, float], time_step, speed) -> float:
        """Updates the orientation to always point in the direction of the current movement vector"""
        next_position = self.update_position(current_position, time_step, speed)
        return degrees(-1 * radians((180 / pi) * (atan2(next_position[1] - current_position[1], next_position[0] - current_position[0]))))

class HorizontalTrajectory(Trajectory):
    def __init__(self, distance_px: float, direction = "left") -> None:
        super().__init__()
        if not isinstance(distance_px, float) and not isinstance(distance_px, int):
            raise ValueError("distance_px must be a int or float")
        if direction not in ["left", "right"]:
            raise ValueError("direction must be 'left' or 'right'")
        self.distance_px_halfed = distance_px/2
        self.direction = direction
        
    def update_position(self, current_position: Tuple[float, float], time_step: float, speed: float) -> Tuple[float, float]:
        if self.direction == "left":
            return ((-speed * time_step) + self.distance_px_halfed, current_position[1])
        else:
            return (speed * time_step - self.distance_px_halfed , current_position[1])

class VerticalTrajectory(Trajectory):
    def __init__(self, distance_px: float, direction = "up") -> None:
        super().__init__()
        if not isinstance(distance_px, float) and not isinstance(distance_px, int):
            raise ValueError("distance_px must be a int or float")
        if direction not in ["up", "down"]:
            raise ValueError("direction must be 'up' or 'down'")
        self.distance_px_halfed = distance_px/2
        self.direction = direction
        
    def update_position(self, current_position: Tuple[float, float], time_step: float, speed: float) -> Tuple[float, float]:
        if self.direction == "up":
            return (current_position[0], (speed * time_step) - self.distance_px_halfed)
        else:
            return (current_position[0], (-speed * time_step) + self.distance_px_halfed)

class DiagonalTrajectory(Trajectory):
    def __init__(self, distance_px: float, direction = "up_right") -> None:
        super().__init__()
        if not isinstance(distance_px, float) and not isinstance(distance_px, int):
            raise ValueError("distance_px must be a int or float")
        if direction not in ["up_right", "up_left", "down_right", "down_left"]:
            raise ValueError("direction must be 'up_right', 'up_left', 'down_right', or 'down_left'")
        self.distance_px_halfed = distance_px/2
        self.direction = direction
        
    def update_position(self, current_position: Tuple[float, float], time_step: float, speed: float) -> Tuple[float, float]:
        if self.direction == "up_right":
            return ((speed * time_step) - self.distance_px_halfed, (speed * time_step) - self.distance_px_halfed)
        elif self.direction == "up_left":
            return ((-speed * time_step) + self.distance_px_halfed, (speed * time_step) - self.distance_px_halfed)
        elif self.direction == "down_right":
            return ((speed * time_step) - self.distance_px_halfed, (-speed * time_step) + self.distance_px_halfed)
        else:
            return ((-speed * time_step) + self.distance_px_halfed, (-speed * time_step) + self.distance_px_halfed)

class CircularTrajectory(Trajectory):
    def __init__(self, radius: float, direction = "clockwise", start: float = 0, monitor: dict = None) -> None:
        super().__init__()
        if not isinstance(radius, float) and not isinstance(radius, int):
            raise ValueError("radius_px must be a int or float")
        if direction not in ["clockwise", "counterclockwise"]:
            raise ValueError("direction must be 'clockwise' or 'counterclockwise'")
        if not isinstance(start, float) and not isinstance(start, int):
            raise ValueError("start must be a int or float")
        if not isinstance(monitor, dict):
            raise ValueError("monitor must be a dict")
        if not "distance" in monitor:
            raise ValueError("monitor must contain a 'distance' key")
        if not "resolution" in monitor:
            raise ValueError("monitor must contain a 'resolution' key")
        if not "height" in monitor:
            raise ValueError("monitor must contain a 'height' key")
        self.monitor = monitor
        self.radius = Utilities.px_to_deg(radius, monitor)
        self.radius = radius
        self.direction = direction
        self.start = start
        
    def update_position(self, 
                        current_position: Tuple[float, float], 
                        time_step: float, 
                        speed: float) -> Tuple[float, float]: # speed is in degrees per second
        if self.direction == "clockwise":
            x = -self.radius * cos(radians(time_step * speed- self.start))
            print(x)
            x = -self.radius * cos(radians(time_step * Utilities.deg_to_px(speed, self.monitor) - self.start))
            print(x, "\n")
            y = self.radius * sin(radians(time_step * Utilities.deg_to_px(speed, self.monitor) - self.start))
            #return (deg_to_px(x, self.monitor), deg_to_px(y, self.monitor))
            return (x, y)
        else:
            x = self.radius * cos(radians(time_step * speed - self.start))
            y = self.radius * sin(radians(time_step * speed - self.start))
            return (Utilities.deg_to_px(x, self.monitor), Utilities.deg_to_px(y, self.monitor))

