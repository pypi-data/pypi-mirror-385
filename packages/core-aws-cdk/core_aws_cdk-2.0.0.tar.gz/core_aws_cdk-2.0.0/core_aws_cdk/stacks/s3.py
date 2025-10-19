# -*- coding: utf-8 -*-

"""S3 stack for bucket infrastructure on AWS."""

from typing import Any, Optional

from aws_cdk import RemovalPolicy
from aws_cdk import aws_s3 as s3

from core_aws_cdk.stacks.base import BaseStack


class BaseS3Stack(BaseStack):
    """ It contains the base elements to create S3 infrastructure on AWS """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def create_bucket(
        self,
        bucket_id: str,
        bucket_name: Optional[str] = None,
        block_public_access: s3.BlockPublicAccess = s3.BlockPublicAccess.BLOCK_ALL,
        removal_policy: Optional[RemovalPolicy] = RemovalPolicy.DESTROY,
        auto_delete_objects: bool = True,
        versioned: bool = False,
        **kwargs: Any
    ) -> s3.Bucket:
        """
        It creates an S3 bucket with associated policy objects....
        https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_s3/Bucket.html
        """

        return s3.Bucket(
            self,
            bucket_id,
            bucket_name=bucket_name,
            block_public_access=block_public_access,
            removal_policy=removal_policy,
            auto_delete_objects=auto_delete_objects,
            versioned=versioned,
            **kwargs)
