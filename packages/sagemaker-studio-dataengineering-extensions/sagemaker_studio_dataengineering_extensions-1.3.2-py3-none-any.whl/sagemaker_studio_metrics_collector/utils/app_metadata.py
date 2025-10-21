import os
from functools import lru_cache
import json
from botocore.session import Session

from sagemaker_studio_metrics_collector.utils.environment_detector import (
    JupyterLabEnvironmentDetector,
)

DEFAULT_REGION = "us-east-2"
SAGEMAKER_RESOURCE_METADATA_FILE = "/opt/ml/metadata/resource-metadata.json"

def get_region_name():
    """Get AWS region name from various sources."""
    region_config_chain = [
        os.environ.get("AWS_REGION"),
        Session().get_scoped_config().get("region"),
        os.environ.get("AWS_DEFAULT_REGION"),
        DEFAULT_REGION,
    ]
    for region_config in region_config_chain:
        if region_config is not None:
            return region_config

def get_partition():
    """Get AWS partition for the current region."""
    return Session().get_partition_for_region(get_region_name())

def _get_app_metadata_file():
    """Read and parse the app metadata file."""
    try:
        with open(SAGEMAKER_RESOURCE_METADATA_FILE) as file:
            return json.loads(file.read())
    except:
        return {}

def get_user_profile_name():
    """Get user profile name from metadata."""
    return _get_app_metadata_file().get("UserProfileName")

def get_shared_space_name():
    """Get shared space name from metadata."""
    return _get_app_metadata_file().get("SpaceName", "")

def get_domain_id():
    """Get domain ID from metadata."""
    return _get_app_metadata_file().get("DomainId")

@lru_cache(maxsize=1)
def get_sagemaker_image():
    """Get SageMaker image information."""
    image_uri = os.environ.get("SAGEMAKER_INTERNAL_IMAGE_URI")
    image_version = os.environ.get("IMAGE_VERSION")
    if image_uri and image_version:
        return f'{image_uri}:{image_version}'
    elif image_uri:
        return f'{image_uri}'
    return "UNKNOWN"

@lru_cache(maxsize=1)
def get_sagemaker_environment():
    return JupyterLabEnvironmentDetector().current_environment
