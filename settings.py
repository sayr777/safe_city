# settings.py
from os.path import join, dirname
from dotenv import load_dotenv
import os
# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')

# Load file from the path.
load_dotenv(dotenv_path)
# print(os.environ['gRPC_URL'])