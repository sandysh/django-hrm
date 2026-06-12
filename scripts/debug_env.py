from decouple import config
import os

print(f"OS Environ DB_HOST: {os.environ.get('DB_HOST')}")
print(f"Decouple DB_HOST: {config('DB_HOST', default='NOT_SET')}")
