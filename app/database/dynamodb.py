import boto3

from app.core.config import settings


def get_dynamodb_resource():
    """
    Create a DynamoDB resource.

    For DynamoDB Local, use dummy credentials.
    For AWS, use the standard Boto3 credential provider chain.
    """

    kwargs = {
        "region_name": settings.aws_region,
    }

    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
        kwargs["aws_access_key_id"] = "local"
        kwargs["aws_secret_access_key"] = "local"

    return boto3.resource("dynamodb", **kwargs)


def get_dynamodb_client():
    """
    Create a low-level DynamoDB client.
    """

    kwargs = {
        "region_name": settings.aws_region,
    }

    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
        kwargs["aws_access_key_id"] = "local"
        kwargs["aws_secret_access_key"] = "local"

    return boto3.client("dynamodb", **kwargs)


def get_table(table_name):
    """
    Return a DynamoDB Table resource.
    """

    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(table_name)
