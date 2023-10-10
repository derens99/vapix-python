from __future__ import annotations
from typing import TYPE_CHECKING

# Import for type hints only
if TYPE_CHECKING:
    from .VapixAPI import VapixAPI

class PTZControl:

    def __init__(self, api: VapixAPI) -> None:
        self.api = api
        
    def get_current_position(self) -> tuple(float, float, float):
        """
        Gets the current position of the camera.

        Returns:
            tuple: A tuple containing the current pan, tilt, and zoom values.
        """
        resp = self.api._send_request('com/ptz.cgi', params={'query': 'position'})
        pan = float(resp.split()[0].split('=')[1])
        tilt = float(resp.split()[1].split('=')[1])
        zoom = float(resp.split()[2].split('=')[1])
        ptz_tuple = (pan, tilt, zoom)

        return ptz_tuple
    
    def absolute_move(self, pan: float, tilt: float, zoom: float, speed: float) -> None:
        """
        Moves the camera to the specified position.

        Args:
            pan (float): The pan value to move to.
            tilt (float): The tilt value to move to.
            zoom (float): The zoom value to move to.
            speed (float): The speed to move at.
        """
        params = {'pan': pan, 'tilt': tilt, 'zoom': zoom, 'speed': speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def relative_move(self, pan: float, tilt: float, zoom: float, speed: float) -> None:
        """
        Moves the camera by the specified amount.

        Args:
            pan (float): The pan value to move by.
            tilt (float): The tilt value to move by.
            zoom (float): The zoom value to move by.
            speed (float): The speed to move at.
        """
        params = {'rpan': pan, 'rtilt': tilt, 'rzoom': zoom, 'speed': speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def continuous_move(self, pan_speed: int, tilt_speed: int, zoom_speed: int) -> None:
        """
        Moves the camera continuously in the specified direction.

        Args:
            pan_speed (int): The pan speed to move at.
            tilt_speed (int): The tilt speed to move at.
            zoom_speed (int): The zoom speed to move at.
        """
        pan_tilt = str(pan_speed) + "," + str(tilt_speed)
        params = {'continuouspantiltmove': pan_tilt, 'continuouszoommove': zoom_speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def continuous_pantilt(self, pan_speed: int, tilt_speed: int) -> None:
        """
        Moves the camera continuously in the specified direction.

        Args:
            pan_speed (int): The pan speed to move at.
            tilt_speed (int): The tilt speed to move at.
        """
        pt_speed = str(pan_speed) + "," + str(tilt_speed)
        params = {'continuouspantiltmove': pt_speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def continuous_zoom(self, zoom_speed: int):
        """
        Moves the camera continuously in the specified direction.

        Args:
            zoom_speed (int): The zoom speed to move at.
        """
        params = {'continuouszoommove': zoom_speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def stop_move(self):
        """
        Stops all movement of the camera.
        """
        self.api._send_request('com/ptz.cgi', params={'continuouspantiltmove': '0,0', 'continuouszoommove': '0'})
        
    def center_move(self, x_pos: int, y_pos: int, speed: int):
        """
        Moves the camera to the specified position.

        Args:
            x_pos (int): The x position to move to.
            y_pos (int): The y position to move to.
            speed (int): The speed to move at.
        """
        params = {'center': str(x_pos) + ',' + str(y_pos), 'speed': speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def area_zoom(self, x_pos: int, y_pos: int, zoom: int, speed: int):
        """
        Moves the camera to the specified position and zoom.

        Args:
            x_pos (int): The x position to move to.
            y_pos (int): The y position to move to.
            zoom (int): The zoom value to move to.
            speed (int): The speed to move at.
        """
        params = {'areazoom': str(x_pos) + ',' + str(y_pos) + ',' + str(zoom), 'speed': speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def move(self, position: str, speed: int):
        """
        Moves the camera to the specified position.

        Args:
            position (str): The position to move to.
            speed (int): The speed to move at.
        """
        params = {'move': position, 'speed': speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def go_home(self, speed: int):
        """
        Moves the camera to the home position.

        Args:
            speed (int): The speed to move at.
        """
        params = {'move': 'home', 'speed': speed}
        self.api._send_request('com/ptz.cgi', params=params)

