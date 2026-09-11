import subprocess
import json
import logging
import os
from pathlib import Path
from .const import CONF_SCHOOL, CONF_USER, CONF_PASS

_LOGGER = logging.getLogger(__name__)

DEFAULT_AUTHCODE = "00000000000000000000000000000000"


class AuthenticationRequired(Exception):
    """Raised when Magister requires re-authentication (invalid password / 2FA)."""

class MagisterAPI:
    def __init__(self, school, user, password, totp_secret: str = None, days_back: int = 0, days_forward: int = 14, history_file: str = None):
        self.school = school
        self.user = user
        self.password = password
        self.totp_secret = totp_secret
        self.days_back = days_back
        self.days_forward = days_forward
        self.history_file = history_file
        self.authcode = DEFAULT_AUTHCODE

    def get_data(self):
        script_dir = Path(__file__).resolve().parent
        script_path = str(script_dir) + "/script/magister.py"
        cmd = [
            "python3", script_path,
            "--json",
            "--schoolserver", f"{self.school}.magister.net",
            "--authcode", self.authcode,
            "--days-back", str(self.days_back),
            "--days-forward", str(self.days_forward),
        ]

        if self.history_file:
            cmd.extend(["--history-file", str(self.history_file)])

        env = dict(os.environ)
        env["MAGISTER_USERNAME"] = self.user
        env["MAGISTER_PASSWORD"] = self.password
        if self.totp_secret:
            env["MAGISTER_TOTP_SECRET"] = self.totp_secret
        else:
            env.pop("MAGISTER_TOTP_SECRET", None)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
                env=env,
            )
            return json.loads(result.stdout)

        except subprocess.TimeoutExpired:
            _LOGGER.error("Magister script timeout")
            raise TimeoutError("Magister script timeout") from None
        except subprocess.CalledProcessError as e:
            _LOGGER.error("Magister script error: %s", e.stderr)
            raise
        except json.JSONDecodeError as e:
            _LOGGER.error("Ongeldige JSON van Magister script: %s", e)
            raise
        except Exception as e:
            _LOGGER.error("Onverwachte fout: %s", e)
            raise
