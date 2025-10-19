# -*- coding: utf-8 -*-

"""Base stack with tagging support for AWS CDK infrastructure."""

from typing import Any, Optional, Dict

from aws_cdk import Stack, Tags
from constructs import Construct


class BaseStack(Stack):
    """
    Contains the base elements to apply to the infrastructure resources
    will be created using on AWS CDK.
    """

    # pylint: disable=redefined-builtin
    def __init__(
        self,
        scope: Construct,
        id: str,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize the BaseStack with optional tags.

        Args:
            scope: The scope in which to define this construct
            id: The scoped construct ID
            tags: Optional dictionary of tags to apply to all resources in this stack
            **kwargs: Additional Stack properties
        """

        super().__init__(scope, id, **kwargs)
        self.tags_dict = tags or {}

        # Apply tags to the stack level (will propagate to all resources)
        for key, value in self.tags_dict.items():
            Tags.of(self).add(key, value)

    def apply_tags(
        self,
        resource: Construct,
        additional_tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Apply tags to a specific resource.

        Args:
            resource: The CDK resource to tag
            additional_tags: Optional additional tags to apply to this resource only
        """
        # Apply base tags
        for key, value in self.tags_dict.items():
            Tags.of(resource).add(key, value)

        # Apply additional tags if provided
        if additional_tags:
            for key, value in additional_tags.items():
                Tags.of(resource).add(key, value)
