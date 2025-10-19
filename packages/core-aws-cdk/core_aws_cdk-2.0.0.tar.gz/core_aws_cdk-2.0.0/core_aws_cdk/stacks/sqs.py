# -*- coding: utf-8 -*-

"""SQS stack for queue infrastructure on AWS."""

from typing import Any, Optional

from aws_cdk import Duration
from aws_cdk import RemovalPolicy
from aws_cdk import aws_sqs as sqs

from core_aws_cdk.stacks.base import BaseStack


class BaseSqsStack(BaseStack):
    """ It contains the base elements to create SQS infrastructure on AWS """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def create_sqs_queue(
        self,
        queue_id: str,
        queue_name: Optional[str],
        receive_message_wait_time: Optional[Duration] = Duration.seconds(20),
        removal_policy: Optional[RemovalPolicy] = RemovalPolicy.DESTROY,
        visibility_timeout: Optional[Duration] = Duration.minutes(5),
        with_dlq: bool = False,
        dlq_id: Optional[str] = None,
        dlq_name: Optional[str] = None,
        max_receive_count: int = 3,
        **kwargs: Any
    ) -> sqs.Queue:
        """
        It creates a new Amazon SQS queue...
        https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_sqs/Queue.html
        """

        dead_letter_queue = None
        if with_dlq:
            if dlq_id is None:
                raise ValueError(
                    "The attribute `dlq_id` is required when `with_dlq` is True!"
                )

            dead_letter_queue = sqs.DeadLetterQueue(
                max_receive_count=max_receive_count,
                queue=sqs.Queue(
                    self,
                    id=dlq_id,
                    queue_name=dlq_name,
                    removal_policy=removal_policy,
                ))

        return sqs.Queue(
            self, queue_id,
            queue_name=queue_name,
            receive_message_wait_time=receive_message_wait_time,
            visibility_timeout=visibility_timeout,
            dead_letter_queue=dead_letter_queue,
            removal_policy=removal_policy,
            **kwargs)
