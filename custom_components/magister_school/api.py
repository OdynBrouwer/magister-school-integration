import subprocess
import json
import logging
import os
import re
import time
from pathlib import Path

from .const import AUTH_FAILED_MARKER, EXIT_AUTH_FAILED

_LOGGER = logging.getLogger(__name__)

DEFAULT_AUTHCODE = "00000000000000000000000000000000"



_SCHOOL_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def normalize_school(value: str | None) -> str | None:
    """Normalize user input to a Magister tenant slug.

    Accepts ``Trevianum``, ``trevianum.magister.net`` and full URLs, and returns
    ``trevianum``. Returns ``None`` when the value cannot be a tenant slug, for
    example because it still contains spaces, ``&`` or another display-name
    character that Magister does not accept in a subdomain.
    """
    if not value:
        return None

    school = str(value).strip().lower()
    school = school.split("://", 1)[-1]
    school = school.split("/", 1)[0].split("?", 1)[0]
    if school.endswith(".magister.net"):
        school = school[: -len(".magister.net")]
    school = school.strip()

    if not _SCHOOL_RE.match(school):
        return None
    return school


class AuthenticationRequired(Exception):
    """Raised when Magister requires re-authentication (invalid password / 2FA)."""

class MagisterAPI:
    def __init__(self, school, user, password, totp_secret: str = None, days_back: int = 0, days_forward: int = 14, history_file: str = None):
        self.school = normalize_school(school) or school
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
                stderr = (err.stderr or "").strip()
                if (
                    err.returncode == EXIT_AUTH_FAILED
                    or AUTH_FAILED_MARKER in stderr
                ):
                    _LOGGER.warning("Magister authentication failed")
                    raise AuthenticationRequired(
                        "Magister authentication failed"
                    ) from None
                if err.returncode != 75:  # EX_TEMPFAIL: retry only script timeouts.
                    _LOGGER.error(
                        "Magister script error (exit %s): %s", err.returncode, stderr
                    )
                    raise
                lines = stderr.splitlines()
                error = lines[-1] if lines else "Magister HTTP request timed out"
            else:
                _LOGGER.debug(
                    "Magister fetch completed in %.1fs", time.monotonic() - started
                )
                data = json.loads(result.stdout)
                if warnings := data.get("data_warnings"):
                    _LOGGER.warning(
                        "Incomplete Magister data (invalid collections/records per section): %s",
                        warnings,
                    )
                return data

            if attempt:
                raise TimeoutError(error) from None
            _LOGGER.debug("%s; retrying once in 2 seconds", error)
            time.sleep(2)
