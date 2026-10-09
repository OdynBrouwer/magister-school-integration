import subprocess
import json
import logging
import os
import time
from pathlib import Path

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

        for attempt in range(2):
            started = time.monotonic()
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=90, check=True, env=env,
                )
            except subprocess.TimeoutExpired:
                # subprocess.run kills and waits for the child before raising.
                error = "Magister script timed out after 90 seconds"
            except subprocess.CalledProcessError as err:
                if err.returncode != 75:  # EX_TEMPFAIL: retry only script timeouts.
                    _LOGGER.error("Magister script error: %s", err.stderr)
                    raise
                lines = (err.stderr or "").strip().splitlines()
                error = lines[-1] if lines else "Magister HTTP request timed out"
            else:
                _LOGGER.debug("Magister fetch completed in %.1fs", time.monotonic() - started)
                return json.loads(result.stdout)

            if attempt:
                raise TimeoutError(error) from None
            _LOGGER.debug("%s; retrying once in 2 seconds", error)
            time.sleep(2)
