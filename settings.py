# configuration settings to avoid run-on commands in docker
import os
from dotenv import load_dotenv

load_dotenv

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379") # default won't work
QUEUES = ["emails", "default"] # default = default queue name

# just do rq -c worker settings to simplify the typing & running
 