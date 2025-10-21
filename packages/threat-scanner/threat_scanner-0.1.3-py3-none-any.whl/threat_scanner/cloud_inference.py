import sys
from typing import Dict
import numpy as np 
from .utils import check_gcloud_auth_explicit

# Import lazily to avoid hard dependency if cloud is not used
_aiplatform = None

def _import_aiplatform():
    global _aiplatform
    if _aiplatform is None:
        try:
            from google.cloud import aiplatform as _aip
            _aiplatform = _aip
        except ImportError:
            raise ImportError("google-cloud-aiplatform is required for cloud inference. Please install it: pip install google-cloud-aiplatform")
    return _aiplatform

def run_cloud_prediction(project_id: str, region: str, endpoint_id: str, gcs_uri: str, label_map: Dict[int, str], time_segment_start: str, time_segment_end: str) -> tuple[str | None, float | None]:
    """
    Performs inference using a Vertex AI endpoint.

    Returns:
        tuple: (predicted_label, confidence_score) or (None, None) if error.
    """
    aiplatform = _import_aiplatform()

    # Check and potentially initiate authentication
    if not check_gcloud_auth_explicit():
        print("Cloud authentication failed or is missing. Cannot proceed with cloud inference.", file=sys.stderr)
        return None, None

    try:
        aiplatform.init(project=project_id, location=region)
        endpoint_name = f"projects/{project_id}/locations/{region}/endpoints/{endpoint_id}"
        endpoint = aiplatform.Endpoint(endpoint_name=endpoint_name)

        instance = {"content": gcs_uri, "mimeType": "video/mp4"}
        if time_segment_start and time_segment_end:
            instance["timeSegmentStart"] = time_segment_start
            instance["timeSegmentEnd"] = time_segment_end
        
        prediction_response = endpoint.predict(instances=[instance])

        # Process response - structure depends on the deployed model's output signature
        if not prediction_response.predictions:
            print("Warning: No predictions returned from the endpoint.", file=sys.stderr)
            return None, None

        first_prediction = prediction_response.predictions[0]
        if isinstance(first_prediction, dict) and 'displayNames' in first_prediction and 'confidences' in first_prediction:
            labels = first_prediction['displayNames']
            confidences = first_prediction['confidences']
            if labels and confidences:
                top_label = labels[0]
                top_confidence = confidences[0]
                return top_label, float(top_confidence)  
        elif isinstance(first_prediction, list):
            if not label_map:
                print("Error: Received raw prediction scores but no label map was provided.", file=sys.stderr)
                return None, None
            probabilities = np.array(first_prediction)
            top_index = np.argmax(probabilities)
            top_confidence = probabilities[top_index]
            top_label = label_map.get(top_index, f"Unknown Class (Index: {top_index})")
            return top_label, float(top_confidence)       
        else:
            print(f"Warning: Unexpected prediction response structure received: {first_prediction}", file=sys.stderr)
            return None, None


    except Exception as e:
        print(f"Error during cloud prediction: {e}", file=sys.stderr)
        return None, None