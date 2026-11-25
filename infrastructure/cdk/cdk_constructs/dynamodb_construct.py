
from aws_cdk import RemovalPolicy, aws_dynamodb as dynamodb
from constructs import Construct


class DynamoDbTables(Construct):
    """
    Reusable construct that creates DynamoDB tables from
    the application's central schema definitions.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        schemas: list[dict],
        stage: str,
    ) -> None:
        super().__init__(scope, construct_id)

        self.tables = {}
        is_prod = stage.lower() == "prod"

        for schema in schemas:
            self._create_table(schema, stage, is_prod)

    def _create_table(
        self,
        schema: dict,
        stage: str,
        is_prod: bool,
    ) -> None:

        base_name = schema["table_name"]
        physical_name = f"{base_name}-{stage}"

        logical_id = "".join(
            part.capitalize()
            for part in physical_name.replace("_", "-").split("-")
        ) + "Table"

        partition_key = schema["partition_key"]
        sort_key = schema.get("sort_key")

        table = dynamodb.Table(
            self,
            logical_id,
            table_name=physical_name,
            partition_key=self._attribute(partition_key),
            sort_key=self._attribute(sort_key) if sort_key else None,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery_specification=(
                dynamodb.PointInTimeRecoverySpecification(
                    point_in_time_recovery_enabled=True,
                    recovery_period_in_days=35,
                )
                if is_prod
                else dynamodb.PointInTimeRecoverySpecification(
                    point_in_time_recovery_enabled=False,
                )
            ),
            deletion_protection=is_prod,
            removal_policy=(
                RemovalPolicy.RETAIN if is_prod
                else RemovalPolicy.DESTROY
            ),
        )

        # Add the GSIs defined in the central schema.
        for index in schema.get("global_secondary_indexes", []):
            gsi_partition_key = index["partition_key"]
            gsi_sort_key = index.get("sort_key")

            table.add_global_secondary_index(
                index_name=index["name"],
                partition_key=self._attribute_by_name(
                    schema, gsi_partition_key
                ),
                sort_key=(
                    self._attribute_by_name(schema, gsi_sort_key)
                    if gsi_sort_key
                    else None
                ),
                projection_type=dynamodb.ProjectionType.ALL,
            )

        self.tables[base_name] = table

    @staticmethod
    def _attribute(key_definition: dict) -> dynamodb.Attribute:
        return dynamodb.Attribute(
            name=key_definition["name"],
            type=DynamoDbTables._attribute_type(
                key_definition["type"]
            ),
        )

    @staticmethod
    def _attribute_by_name(
        schema: dict,
        attribute_name: str,
    ) -> dynamodb.Attribute:

        definitions = {}

        definitions.update(schema.get("source_attributes", {}))
        definitions.update(schema.get("derived_attributes", {}))

        # Include simple attributes from schemas that use "attributes".
        for name, definition in schema.get("attributes", {}).items():
            if isinstance(definition, str):
                definitions[name] = definition

        # Base table keys are also valid GSI keys.
        partition_key = schema["partition_key"]
        definitions[partition_key["name"]] = partition_key["type"]

        sort_key = schema.get("sort_key")
        if sort_key:
            definitions[sort_key["name"]] = sort_key["type"]

        if attribute_name not in definitions:
            raise ValueError(
                f"Attribute '{attribute_name}' is not defined "
                f"in schema '{schema['table_name']}'"
            )

        return dynamodb.Attribute(
            name=attribute_name,
            type=DynamoDbTables._attribute_type(
                definitions[attribute_name]
            ),
        )

    @staticmethod
    def _attribute_type(type_name: str) -> dynamodb.AttributeType:
        type_mapping = {
            "STRING": dynamodb.AttributeType.STRING,
            "NUMBER": dynamodb.AttributeType.NUMBER,
            "BINARY": dynamodb.AttributeType.BINARY,
        }

        if type_name not in type_mapping:
            raise ValueError(
                f"Unsupported DynamoDB key type: {type_name}"
            )

        return type_mapping[type_name]
