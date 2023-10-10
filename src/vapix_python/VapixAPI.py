import time
import requests

from .PTZControl import PTZControl

from requests.auth import HTTPDigestAuth

class VapixAPI:
    
    def __init__(self, host, user, password, timeout=5):
        self.host = host
        self.user = user
        self.password = password
        
        self.base_url = 'http://' + self.host + '/axis-cgi'
        
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(self.user, self.password)
        self.session.timeout = timeout
        
        self.ptz = PTZControl(self)
        
    def _send_request(self, endpoint, method="GET", params=None):
        url = f"{self.base_url}/{endpoint}"
        base_args = {
            'camera': '1',
            'html': 'no',
            'timestamp': int(time.time()),
        }
        
        if params:
            base_args.update(params)
        
        try:
            if method == "GET":
                response = self.session.get(url, params=base_args)
            elif method == "POST":
                response = self.session.post(url, data=base_args)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise e
        

        
        
if __name__ == '__main__':
    import time
    import os
    import dotenv
    dotenv.load_dotenv()
    v = VapixAPI(os.environ.get('host'), os.environ.get('user'), os.environ.get('password'))
    print(v.ptz.get_current_position())
