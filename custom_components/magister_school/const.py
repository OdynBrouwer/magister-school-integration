DOMAIN = "magister_school"
CONF_SCHOOL = "school"
CONF_USER = "user"
CONF_PASS = "pass"
DEFAULT_NAME = "Magister Data"

# Polling interval in seconds (15 minutes, matches the historical behaviour).
DEFAULT_POLL_INTERVAL = 900
MIN_POLL_INTERVAL = 60
MAX_POLL_INTERVAL = 86400

# Exit code used by script/magister.py when authentication fails, so the
# integration can distinguish a login problem from other script errors.
EXIT_AUTH_FAILED = 77
AUTH_FAILED_MARKER = "AUTHENTICATION_FAILED"
