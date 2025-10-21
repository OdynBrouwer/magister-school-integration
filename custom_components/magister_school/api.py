import subprocess
import json
import logging
from .const import CONF_SCHOOL, CONF_USER, CONF_PASS

_LOGGER = logging.getLogger(__name__)

DEFAULT_AUTHCODE = "00000000000000000000000000000000"

class MagisterAPI:
    def __init__(self, school, user, password):
        self.school = school
        self.user = user
        self.password = password
        self.authcode = DEFAULT_AUTHCODE

    def get_data(self):
        script_path = "/config/custom_components/magister_school/magister.py"
        cmd = [
            "python3", script_path,
            "--json",
            "--schoolserver", f"{self.school}.magister.net",
            "--username", self.user,
            "--password", self.password,
            "--authcode", self.authcode
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,
                check=True
            )
            return json.loads(result.stdout)
            
        except subprocess.TimeoutExpired:
            _LOGGER.error("Magister script timeout")
            raise
        except subprocess.CalledProcessError as e:
            _LOGGER.error("Magister script error: %s", e.stderr)
            raise
        except json.JSONDecodeError as e:
            _LOGGER.error("Ongeldige JSON van Magister script: %s", e)
            raise
        except Exception as e:
            _LOGGER.error("Onverwachte fout: %s", e)
            raise
