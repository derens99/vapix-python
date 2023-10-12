import time
import requests

from .PTZControl import PTZControl
from .GeolocationAPI import GeolocationAPI

from requests.auth import HTTPDigestAuth

class VapixAPI:
    """
    A class that provides an interface to interact with Axis cameras using the VAPIX API.

    Attributes:
    -----------
    host : str
        IP address or domain name of the camera.
    user : str
        Username for the camera's API authentication.
    password : str
        Password for the camera's API authentication.
    base_url : str
        Base URL for accessing the VAPIX API endpoints.
    session : requests.Session
        Session object for handling HTTP requests with authentication.
    ptz : PTZControl
        Instance for controlling Pan-Tilt-Zoom features of the camera.
    geolocation : GeolocationAPI
        Instance for handling camera's geolocation functionalities.
    """

    def __init__(self, host, user, password, timeout=5):
        """
        Initializes the VapixAPI with host, user, and password credentials.

        Parameters:
        -----------
        host : str
            IP address or domain name of the camera.
        user : str
            Username for the camera's API authentication.
        password : str
            Password for the camera's API authentication.
        timeout : int, optional
            Timeout for HTTP requests (default is 5 seconds).
        """
        self.host = host
        self.user = user
        self.password = password
        self.base_url = 'http://' + self.host + '/axis-cgi'
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(self.user, self.password)
        self.session.timeout = timeout
        self.ptz = PTZControl(self)
        self.geolocation = GeolocationAPI(self)

    def _send_request(self, endpoint, method="GET", params=None, base_args=True):
        """
        Send a request to a specific VAPIX API endpoint with base arguments.

        Parameters:
        -----------
        endpoint : str
            The endpoint to which the request is sent.
        method : str, optional
            HTTP request method (default is "GET").
        params : dict, optional
            Parameters to be included in the request.
        base_args : bool, optional
            Flag to decide if base arguments need to be included (default is True).

        Returns:
        --------
        str
            Response text from the request.

        Raises:
        -------
        requests.RequestException
            If the request encounters an error.
        """
        url = f"{self.base_url}/{endpoint}"
        base_args_dict = {
            'camera': '1',
            'html': 'no',
            'timestamp': int(time.time()),
        }
        
        if params:
            base_args_dict.update(params)
        
        try:
            if method == "GET":
                response = self.session.get(url, params=base_args_dict)
            elif method == "POST":
                response = self.session.post(url, data=base_args_dict)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise e
        
    def _send_request_vanilla(self, endpoint, method="GET", params=None):
        """
        Send a request to a specific VAPIX API endpoint without base arguments.

        Parameters:
        -----------
        endpoint : str
            The endpoint to which the request is sent.
        method : str, optional
            HTTP request method (default is "GET").
        params : dict, optional
            Parameters to be included in the request.

        Returns:
        --------
        str
            Response text from the request.

        Raises:
        -------
        requests.RequestException
            If the request encounters an error.
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                response = self.session.post(url, data=params)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise e

        
        
if __name__ == '__main__':
    import time
    import os
    import dotenv
    dotenv.load_dotenv()
    vapix_api = VapixAPI(os.environ.get('host'), os.environ.get('user'), os.environ.get('password'))

    print(vapix_api.ptz.get_current_position())
    
    vapix_api.session.close()