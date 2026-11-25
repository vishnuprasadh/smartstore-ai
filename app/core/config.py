import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    aws_region : str
    dynamodb_endpoint_url : str | None
    products_table_name : str
    
    @classmethod
    def from_environment(cls):
        return cls(
                aws_region = os.getenv("AWS_DEFAULT_REGION","ap-south-1" ),
                dynamodb_endpoint_url=os.getenv("DYNAMODB_ENDPOINT_URL"),
                products_table_name=os.getenv("PRODUCTS_TABLE_NAME","products")
        )


settings = Settings.from_environment()
