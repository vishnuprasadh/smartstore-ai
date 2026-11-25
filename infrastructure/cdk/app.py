#!/usr/bin/env python3

import os
import sys
from pathlib import Path

import aws_cdk as cdk

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.dynamodb.products_table import PRODUCTS_TABLE
from infrastructure.dynamodb.stores_table import STORES_TABLE
from infrastructure.dynamodb.item_listings_table import ITEM_LISTINGS_TABLE
from infrastructure.dynamodb.item_listing_history_table import (
    ITEM_LISTING_HISTORY_TABLE,
)

from cdk.cdk_stack import SmartStoreStack

app = cdk.App()

stage = (
    app.node.try_get_context("stage")
    or os.getenv("SMARTSTORE_STAGE")
    or "dev"
)

schemas = [
    PRODUCTS_TABLE,
    STORES_TABLE,
    ITEM_LISTINGS_TABLE,
    ITEM_LISTING_HISTORY_TABLE,
]

environment = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "ap-south-1"),
)

SmartStoreStack(
    app,
    f"SmartStore-{stage}",
    stage=stage,
    schemas=schemas,
    env=environment,
    description=f"SmartStore DynamoDB infrastructure - {stage}",
)

app.synth()
