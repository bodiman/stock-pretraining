import os
from dotenv import load_dotenv

# Load environmental variables from a .env file
load_dotenv()

# Define a function to get the value of an environmental variable
def get_env_variable(variable_name, default=None):
    return os.getenv(variable_name, default)
