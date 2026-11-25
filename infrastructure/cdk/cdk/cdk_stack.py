
from aws_cdk import Stack
from constructs import Construct

from cdk_constructs.dynamodb_construct import DynamoDbTables


class SmartStoreStack(Stack):
    """
    SmartStore infrastructure stack.

    Creates the DynamoDB resources for the selected environment.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        stage: str,
        schemas: list[dict],
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        if stage not in {"dev", "test", "staging", "prod"}:
            raise ValueError(
                f"Unsupported stage '{stage}'. "
                "Use dev, test, staging, or prod."
            )

        self.dynamodb_tables = DynamoDbTables(
            self,
            "SmartStoreDynamoDbTables",
            schemas=schemas,
            stage=stage,
        )
