import json
import os
import sys
import subprocess
import importlib.util
import google.auth
from importlib import resources

# Define classes identified as threats by the default model (adjust as needed)
# Based on Kinetics 700 labels that might imply threat
THREAT_CLASSES = [
    "shooting target", "shooting bow and arrow", "sword fighting",
    "wrestling", "punching person (boxing)", "punching bag", "slapping",
    "kicking", "fencing", "throwing axe", "setting fire", "lighting fire",
    "rioting", "smashing"
]

DEFAULT_MODEL_DIR_NAME = 'default_model'

def get_default_model_path():
    """Gets the path to the default model packaged with the library."""
    try:
        # Find the path relative to this utils.py file
        package_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(package_dir, DEFAULT_MODEL_DIR_NAME)
        # Basic check if the model directory seems present
        if os.path.isdir(model_path) and os.path.exists(os.path.join(model_path, 'saved_model.pb')):
            return model_path
        else:
            print(f"Warning: Default model directory not found or incomplete at {model_path}. Local inference with default model will fail.", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Warning: Error locating default model path: {e}", file=sys.stderr)
        return None

def load_label_map(custom_map_path: str = None) -> dict[int, str] | None:
    """
    Loads a label map from a JSON file.

    If a custom_map_path is provided, it loads from that file.
    Otherwise, it loads the default kinetics_600_labels.json from the package.
    """
    try:
        if custom_map_path:
            print(f"Loading custom label map from: {custom_map_path}")
            with open(custom_map_path, "r") as f:
                json_data = json.load(f)
        else:
            print("Loading default Kinetics 600 label map from package.")
            with resources.open_text('threat_scanner', 'kinetics_600_labels.json') as f:
                json_data = json.load(f)

        # Convert string keys from JSON to integer keys to match numpy's argmax output
        label_map = {int(k): v for k, v in json_data.items()}
        return label_map
    except:
        print("fyi: No label map was provided")

def load_config(config_path: str) -> dict:
    """Loads configuration from a JSON file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in configuration file: {config_path}")
    except Exception as e:
        raise IOError(f"Error reading configuration file {config_path}: {e}")

def check_gcloud_auth_explicit():
    """
    Checks if Google Cloud ADC are available.
    If not, attempts to run the login command.
    """
    try:
        credentials, project = google.auth.default()
        print(f"Google Cloud authentication found for project: {project}")
        return True
    except google.auth.exceptions.DefaultCredentialsError:
        print("Google Cloud authentication not found.")
        print("Attempting to run 'gcloud auth application-default login'...")
        try:
            # Check if gcloud CLI is installed
            if not importlib.util.find_spec("google.cloud.storage"): # Check indirectly
                 print("Warning: google-cloud-sdk (gcloud) might not be installed or in PATH.", file=sys.stderr)
                 print("Please run 'gcloud auth application-default login' manually in your terminal.", file=sys.stderr)
                 return False

            # Run the gcloud login command - This requires user interaction in the terminal
            process = subprocess.run(['gcloud', 'auth', 'application-default', 'login'], check=False)

            if process.returncode == 0:
                print("Authentication successful (pending browser verification). Please restart the script if needed.")
                # Re-check credentials after login attempt
                try:
                     google.auth.default()
                     return True
                except google.auth.exceptions.DefaultCredentialsError:
                     print("Authentication still not detected after login attempt. Manual login required.", file=sys.stderr)
                     return False
            else:
                print("gcloud auth command failed or was cancelled.", file=sys.stderr)
                print("Please run 'gcloud auth application-default login' manually in your terminal.", file=sys.stderr)
                return False
        except FileNotFoundError:
             print("Error: 'gcloud' command not found. Is Google Cloud SDK installed and in your PATH?", file=sys.stderr)
             print("Please run 'gcloud auth application-default login' manually.", file=sys.stderr)
             return False
        except Exception as e:
            print(f"An unexpected error occurred during authentication check: {e}", file=sys.stderr)
            print("Please run 'gcloud auth application-default login' manually.", file=sys.stderr)
            return False

def get_threat_level_color(confidence: float) -> str:
    """Determines HTML color based on confidence."""
    if confidence >= 0.8:
        return "red"       # High confidence threat
    elif confidence >= 0.5:
        return "orange"    # Medium confidence threat
    else:
        return "black"     # Lower confidence or non-threat