#!/usr/bin/env python3
import sys
sys.path.insert(0, 'custom_components/magister_school')

# Patch sys.argv
sys.argv = [
    'magister.py',
    '--debug',
    '--schoolserver', 'trevianum.magister.net',
    '--username', 'rbrouwer',
    '--password', 'Mupsje117882!'
]

# Import and run
from magister import main
try:
    main()
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
