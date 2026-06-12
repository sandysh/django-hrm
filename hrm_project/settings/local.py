from .base import *

# Local development overrides

DEBUG = config('DEBUG', default=True, cast=bool)

# Add any additional local-only settings here
