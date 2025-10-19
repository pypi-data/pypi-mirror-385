# -*- coding: utf-8 -*-

"""SNS stack for topic and notification infrastructure on AWS."""

from typing import Any, Optional

from aws_cdk import aws_sns as sns

from core_aws_cdk.stacks.base import BaseStack


class BaseSnsStack(BaseStack):
    """ It contains the base elements to create SNS infrastructure on AWS """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def create_sns_topic(
        self,
        topic_id: str,
        topic_name: Optional[str] = None,
        display_name: Optional[str] = None,
        fifo: Optional[bool] = None,
        content_based_deduplication: Optional[bool] = None,
        **kwargs: Any
    ) -> sns.Topic:
        """
        It creates a new SNS topic...
        https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_sns/Topic.html
        """

        return sns.Topic(
            self,
            topic_id,
            topic_name=topic_name,
            content_based_deduplication=content_based_deduplication,
            display_name=display_name,
            fifo=fifo,
            **kwargs)
