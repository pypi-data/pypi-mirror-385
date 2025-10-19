# -*- coding: utf-8 -*-

"""Lambda stack for serverless function infrastructure on AWS."""

from typing import Any, Dict, Optional, List

from aws_cdk import Duration
from aws_cdk import aws_lambda
from aws_cdk.aws_lambda import Architecture
from aws_cdk.aws_lambda import Code
from aws_cdk.aws_lambda import IEventSource
from aws_cdk.aws_lambda import Runtime

from core_aws_cdk.stacks.base import BaseStack


class BaseLambdaStack(BaseStack):
    """ It contains the base elements to create Lambda infrastructure on AWS """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def create_lambda(
        self,
        function_id: str,
        handler: str,
        code: Code,
        runtime: Runtime = Runtime.PYTHON_3_12,
        architecture: Architecture = Architecture.ARM_64,
        timeout: Duration = Duration.minutes(5),
        event_sources: Optional[List[IEventSource]] = None,
        environment: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> aws_lambda.Function:
        """
        It deploys a package on AWS Lambda service...

        If your function just need to copy the content of a folder
        then code attribute would be:

        .. code-block:: python

            code = aws_lambda.Code.from_asset("path_to_folder_to_deploy")
        ..

        Another option is the use of the class "AssetCode" from
        package "aws_cdk.aws_lambda" that contains useful methods to load
        the code from different sources like:

          - from_docker_build: Loads the function code from an
            asset created by a Docker build.
          - from_cfn_parameters: Creates a new Lambda source
            defined using CloudFormation parameters.
          - from_bucket: Lambda handler code as an S3 object.
          - from_inline: Inline code for Lambda handler.
          - from_asset: Loads the function code from a local
            disk path.
          - from_ecr_image: Use an existing ECR image as the
            Lambda code.
          - from_asset_image: Create an ECR image from the
            specified asset and bind it as the Lambda code.

        If your function requires specific dependencies, or you need to decrease the size
        of the package by removing useless or not required folders and files, you could use the
        following mechanism (*** AVAILABLE FOR PYTHON ONLY ***):

        .. code-block:: python

            from core_aws_cdk.stacks.lambda_fcn.assets import ZipAssetCode

            self.create_lambda(
                function_id="MockService-Function",
                function_name="Lambda-Name",
                description="description...",
                code=ZipAssetCode(
                    project_directory=pathlib.Path("/path_to/project"),
                    work_dir=pathlib.Path("/path_to/project/lambdas/lambda_folder"),
                    include_project_folders=[
                        "common_folder",
                        "file1.py"
                    ],
                    include_paths=[
                        "some_folder",
                        "__init__.py",
                        "handler.py"
                    ]
                ),
                handler="handler.handler",
                role=service_role
            )
        ..
        """

        fcn = aws_lambda.Function(
            scope=self,
            id=function_id,
            handler=handler,
            code=code,
            runtime=runtime,
            architecture=architecture,
            timeout=timeout,
            environment=environment,
            **kwargs)

        if event_sources:
            for source in event_sources:
                fcn.add_event_source(source)

        # Apply tags (stack-level tags + function-specific tags)
        if tags:
            self.apply_tags(fcn, additional_tags=tags)

        return fcn
