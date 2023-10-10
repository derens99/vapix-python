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
    
    def get_current_ptz(self) -> str:
        """
        Gets the current position of the camera.

        Returns:
            str: A string containing the current pan, tilt, and zoom values.
        """
        resp = self.api._send_request('com/ptz.cgi', params={'query': 'position'})
        return resp
    
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
        
    def continuous_focus(self, focus_speed: int):
        """
        Moves the camera continuously in the specified direction.

        Args:
            focus_speed (int): The focus speed to move at.
        """
        params = {'continuousfocusmove': focus_speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def continuous_iris(self, iris_speed: int):
        """
        Moves the camera continuously in the specified direction.

        Args:
            iris_speed (int): The iris speed to move at.
        """
        params = {'continuousirismove': iris_speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def continuous_brightness(self, brightness_speed: int):
        """
        Moves the camera continuously in the specified direction.

        Args:
            brightness_speed (int): The brightness speed to move at.
        """
        params = {'continuousbrightnessmove': brightness_speed}
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
        
    def set_move_speed(self, speed: int):
        """
        Sets the speed of the camera.

        Args:
            speed (int): The speed to move at.
        """
        if speed < 0 or speed > 100:
            raise ValueError("Speed must be between 0 and 100.")
        params = {'speed': speed}
        self.api._send_request('com/ptz.cgi', params=params)
        
    def go_home(self, speed: int):
        """
        Moves the camera to the home position.

        Args:
            speed (int): The speed to move at.
        """
        params = {'move': 'home', 'speed': speed}
        self.api._send_request('com/ptz.cgi', params=params)

    def ptz_enabled(self, channel: int = 1):
        """
        Checks if PTZ is enabled on the camera.

        Args:
            channel (int, optional): The channel to check. Defaults to 1.

        Returns:
            str: List of available commands if enabled, empty string if disabled.
        """
        resp = self.api._send_request('com/ptz.cgi', params={'info': channel, 'camera': 1})
        return resp
    
    def set_iris(self, iris_level: int = 1750) -> bool:
        """
        Sets the iris to the specified value.

        Args:
            enabled (bool, optional): Whether to enable or disable the iris. Defaults to True.
        """
        if iris_level < 0 or iris_level > 9999:
            raise ValueError("Iris level must be between 0 and 9999.")
        params = {'iris': iris_level}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def set_focus(self, focus_level: int) -> bool:
        """
        Sets the focus to the specified value.

        Args:
            focus_level (int): The focus level to set.
        """
        if focus_level < 0 or focus_level > 9999:
            raise ValueError("Focus level must be between 0 and 9999.")
        params = {'focus': focus_level}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def set_zoom(self, zoom_level: int) -> bool:
        """
        Sets the zoom to the specified value.

        Args:
            zoom_level (int): The zoom level to set.
        """
        if zoom_level < 0 or zoom_level > 9999:
            raise ValueError("Zoom level must be between 0 and 9999.")
        params = {'zoom': zoom_level}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def set_brightness(self, brightness_level: int) -> bool:
        """
        Sets the brightness to the specified value.

        Args:
            brightness_level (int): The brightness level to set.
        """
        if brightness_level < 0 or brightness_level > 9999:
            raise ValueError("Brightness level must be between 0 and 9999.")
        params = {'brightness': brightness_level}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def set_autofocus(self, enabled: bool = True):
        """
        Enables or disables autofocus.

        Args:
            enabled (bool, optional): Whether to enable or disable autofocus. Defaults to True.
        """
        if enabled:
            enabled = 'on'
        else:
            enabled = 'off'
        params = {'autofocus': enabled}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def set_autoiris(self, enabled: bool = True):
        """
        Enables or disables autoiris.

        Args:
            enabled (bool, optional): Whether to enable or disable autoiris. Defaults to True.
        """
        if enabled:
            enabled = 'on'
        else:
            enabled = 'off'
        params = {'autoiris': enabled}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def set_current_preset_name(self, preset_name):
        """
        Associates the current position to <preset name> as a preset position in the Axis product.

        Args:
            preset_name (str): The name of the preset to set.
        """
        params = {'setserverpresetname': preset_name}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def set_current_preset_no(self, preset_number):
        """
        Saves the current position as a preset position number in the Axis product.

        Args:
            preset_number (int): The number of the preset to set.
        """
        params = {'setserverpresetno': preset_number}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def rename_preset_number(self, preset_number, preset_name):
        """
        Renames a preset position number in the Axis product.

        Args:
            preset_number (int): The number of the preset to rename.
            preset_name (str): The new name of the preset.
        """
        params = {'renameserverpresetno': preset_name, 'newname': preset_number}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def set_home(self):
        """
        Sets the current position as the home position.
        """
        self.api._send_request('com/ptz.cgi', params={'home': 'yes'})
        return True
    
    def remove_server_preset_name(self, preset_name):
        """
        Removes a preset position name from the Axis product.

        Args:
            preset_name (str): The name of the preset to remove.
        """
        params = {'removeserverpresetname': preset_name}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def remove_server_preset_no(self, preset_number):
        """
        Removes a preset position number from the Axis product.

        Args:
            preset_number (int): The number of the preset to remove.
        """
        params = {'removeserverpresetno': preset_number}
        self.api._send_request('com/ptz.cgi', params=params)
        return True
    
    def set_device_preset(self, preset_number):
        """
        Bypasses the presetpos interface and tells the device to save its current position as preset position 
        <preset pos> directly in the device, where <preset pos> is a device-specific preset position number. 
        This may also be a device-specific special function.

        Args:
            preset_number (int): The number of the preset to move to.
        """
        params = {'setdevicepreset': preset_number}
        self.api._send_request('com/ptz.cgi', params=params)
        return True