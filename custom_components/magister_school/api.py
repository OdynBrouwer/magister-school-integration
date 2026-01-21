import subprocess
import json
import logging
from pathlib import Path
from .const import CONF_SCHOOL, CONF_USER, CONF_PASS

_LOGGER = logging.getLogger(__name__)

DEFAULT_AUTHCODE = "00000000000000000000000000000000"

class AuthenticationRequired(Exception):
    """Raised when Magister requires re-authentication (e.g. password change)."""
    pass

class MagisterAPI:
    def __init__(self, school, user, password):
        self.school = school
        self.user = user
        self.password = password
        self.authcode = DEFAULT_AUTHCODE

    def get_data(self):
        script_dir = Path(__file__).resolve().parent
        script_path = str(script_dir) + "/magister.py"
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
                check=True,
            )
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                out = (result.stdout or "") + (result.stderr or "")
                _LOGGER.error("Ongeldige JSON van Magister script: %s, output: %s", e, out)
                low = out.lower()
                if any(tok in low for tok in ["visit website", "redirect url does not contain a fragment", "could not get account info", "requested -> visit website", "change password"]):
                    raise AuthenticationRequired(out)
                raise

        except subprocess.TimeoutExpired:
            _LOGGER.error("Magister script timeout")
            raise
        except subprocess.CalledProcessError as e:
            out = (e.stdout or "") + (e.stderr or "")
            _LOGGER.error("Magister script error: %s", out)
            low = out.lower()
            if any(tok in low for tok in ["visit website", "redirect url does not contain a fragment", "could not get account info", "requested -> visit website", "change password"]):
                raise AuthenticationRequired(out)
            raise
        except Exception as e:
            _LOGGER.error("Onverwachte fout: %s", e)
            raise
