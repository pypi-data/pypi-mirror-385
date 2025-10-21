import os
from async_lru import alru_cache
from sagemaker_studio_metrics_collector.utils.aws_clients import get_caller_identity
from sagemaker_studio_metrics_collector.utils.app_metadata import get_region_name

@alru_cache(maxsize=1)
async def get_aws_account_id():
    """Get AWS account ID from environment or STS.

    First checks AWS_ACCOUNT_ID environment variable,
    if not found, calls STS get_caller_identity.

    Returns:
        str: AWS account ID
    """
    accountId = os.environ.get("AWS_ACCOUNT_ID")
    if accountId is None:
        response = await get_caller_identity(get_region_name())
        accountId = response.get("Account")
    return accountId
