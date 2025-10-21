import botocore
from aiobotocore.session import get_session
from typing import Dict

async def get_caller_identity(region_name: str) -> Dict:
    """Get caller identity from AWS STS.

    Args:
        region_name: AWS region name

    Returns:
        Dict containing caller identity information
    """
    session = get_session()
    config = botocore.client.Config(
        connect_timeout=10,
        read_timeout=20,
        retries={"max_attempts": 2}
    )

    async with session.create_client(
        service_name="sts",
        config=config,
        region_name=region_name
    ) as sts:
        return await sts.get_caller_identity()
