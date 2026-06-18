from .base import *

DEBUG = True

# Example: ALLOWED_HOSTS = allwed host put here 
# and other production settings 
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0').split(',')

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000/",
    "http://127.0.0.1:3000/",
    "https://hrm.darkmatterproduction.org/"
]