import json
from .cache import ttl_cache


@ttl_cache(ttl_seconds=60)
def retrieve_sagemaker_metadata_from_file(logger=None):
    try:
        # Opening JSON file
        with open('/opt/ml/metadata/resource-metadata.json') as f:
            metadata = json.load(f)
            return metadata
    except Exception as e:
        if logger is not None:
            logger.error(f"Unable to retrieve sagemaker metadata from file: {e}")
        return None


@ttl_cache(ttl_seconds=60)
def retrieve_sagemaker_storage_metadata_from_file(logger=None):
    try:
        # Opening JSON file
        with open('/home/sagemaker-user/.config/smus-storage-metadata.json') as f:
            metadata = json.load(f)
            return metadata
    except Exception as e:
        if logger is not None:
            logger.error(f"Unable to retrieve sagemaker storage metadata from file: {e}")
        return None
    

def get_app_type() -> str:
    resource_metadata = retrieve_sagemaker_metadata_from_file()
    return resource_metadata.get("AppType") if resource_metadata else None
