import os
import sys
from typing import Optional, Dict, Any, Tuple
from .utils import load_config, THREAT_CLASSES, get_default_model_path, load_label_map
from .cloud_inference import run_cloud_prediction
from .email_alert import send_threat_email

class ThreatDetector:
    """
    Detects threats in videos using local or cloud-based models.
    """
    def __init__(self,
                 email_params: Optional[Dict[str, str]] = None,
                 cloud_params: Optional[Dict[str, str]] = None,
                 config_path: Optional[str] = None,
                 label_map_path: Optional[str] = None):
        """
        Initializes the ThreatDetector.

        Configuration is loaded with the following precedence:
        1.  Content from the `config_path` JSON file.
        2.  Direct keyword arguments (which will override any values from the config file).

        Args:
            cloud_params (Dict, optional): Dictionary with cloud config. Must contain:
                'project_id', 'region', 'endpoint_id', 'gcs_uri'.
                Can optionally contain 'timeSegmentStart' and 'timeSegmentEnd'.
            email_params (Dict, optional): Dictionary with email config:
                {'api_key', 'recipient_email', 'sender_email'}.
            config_path (str, optional): Path to a JSON configuration file.
            label_map_path (str, optional): Path to a custom JSON label map file.
        """
        self.email_params: Optional[Dict[str, str]] = None
        self.cloud_params: Optional[Dict[str, str]] = None
        self.threat_classes = THREAT_CLASSES
        self.label_map: Optional[Dict[int, str]] = None
        
        if config_path:
            print(f"Loading configuration from: {config_path}")
            try:
                config = load_config(config_path)
                self.email_params = config.get('email_params')
                self.cloud_params = config.get('cloud_params')
                self.threat_classes = config.get('threat_classes', THREAT_CLASSES)
                label_map_path = config.get('label_map_path', label_map_path)
            except (FileNotFoundError, ValueError) as e:
                print(f"Warning: Could not load config file '{config_path}': {e}", file=sys.stderr)

        # Override with direct arguments
        if email_params is not None: self.email_params = email_params
        if cloud_params is not None: self.cloud_params = cloud_params

        # Validate cloud parameters are present
        if not self.cloud_params or not all(k in self.cloud_params for k in ['project_id', 'region', 'endpoint_id', 'gcs_uri']):
            raise ValueError("Missing required configuration. 'cloud_params' (with project_id, region, endpoint_id, and gcs_uri) must be provided either directly or via a config file.")
        
        # Load the label map
        self.label_map = load_label_map(label_map_path)
        if not self.label_map:
            raise RuntimeError("Failed to load a valid label map. Cannot proceed.")

        # Validate email params if API key is present
        if self.email_params and self.email_params.get('api_key'):
            if not self.email_params.get('recipient_email') or not self.email_params.get('sender_email'):
                print("Warning: Email API key provided, but recipient or sender email is missing. Alerts will be disabled.", file=sys.stderr)
                self.email_params['api_key'] = None # Disable alerts


    def detect(self) -> Tuple[Optional[str], Optional[float], bool]:
        """
        Runs threat detection on the configured video.

        Returns:
            tuple: (predicted_label, confidence_score, is_threat)
                   Returns (None, None, False) if inference fails.
        """
        if not self.cloud_params:
            print("Error: Cloud parameters are not configured.", file=sys.stderr)
            return None, None, False

        predicted_label, confidence = run_cloud_prediction(
                project_id=self.cloud_params['project_id'],
                region=self.cloud_params['region'],
                endpoint_id=self.cloud_params['endpoint_id'],
                gcs_uri=self.cloud_params['gcs_uri'],
                label_map=self.label_map,
                time_segment_start=self.cloud_params['time_segment_start'],
                time_segment_end=self.cloud_params['time_segment_end']
            )

        is_threat = False
        if predicted_label is not None and confidence is not None:
            if predicted_label.lower() in [t.lower() for t in self.threat_classes]:
                is_threat = True
                print(f"Threat Detected: '{predicted_label}' (Confidence: {confidence:.2f})")

                if self.email_params:
                    send_threat_email(
                        api_key=self.email_params['api_key'],
                        from_email=self.email_params['sender_email'],
                        to_email=self.email_params['recipient_email'],
                        video_ref=self.cloud_params['gcs_uri'],
                        threat_label=predicted_label,
                        confidence=confidence
                    )
            else:
                print(f"No threat detected. Top prediction: '{predicted_label}' (Confidence: {confidence:.2f})")
        else:
            print("Inference failed or returned no result.")
            return None, None, False

        return predicted_label, confidence, is_threat
