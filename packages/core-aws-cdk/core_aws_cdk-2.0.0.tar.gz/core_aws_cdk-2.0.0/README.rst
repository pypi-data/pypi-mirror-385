===============================================================================
core-aws-cdk
===============================================================================

This project contains common elements and constructs to create infrastructure
in AWS using AWS CDK with Python.


.. image:: https://img.shields.io/pypi/pyversions/core-aws-cdk.svg
    :target: https://pypi.org/project/core-aws-cdk/
    :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-aws-cdk/-/blob/main/LICENSE
    :alt: License

.. image:: https://gitlab.com/bytecode-solutions/core/core-aws-cdk/badges/release/pipeline.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-aws-cdk/-/pipelines
    :alt: Pipeline Status

.. image:: https://readthedocs.org/projects/core-aws-cdk/badge/?version=latest
    :target: https://readthedocs.org/projects/core-aws-cdk/
    :alt: Docs Status

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
    :alt: Security

|

Features
===============================================================================

* **Base Stacks**: Pre-configured CDK stacks with tagging support
* **Lambda Functions**: Simplified Lambda creation with automatic packaging
* **S3 Buckets**: S3 bucket creation with security best practices
* **SQS Queues**: Queue creation with dead-letter queue support
* **SNS Topics**: Topic creation with subscription management
* **Network Stack**: VPC and networking resource management
* **ZIP Asset Packaging**: Automatic Lambda ZIP creation with dependencies
* **Comprehensive Testing**: Unit, functional, and integration tests
* **Parallel Test Execution**: Fast test runs with pytest-xdist

Installation
===============================================================================

Basic Installation
---------------------------------------

.. code-block:: shell

    pip install core-aws-cdk

..

Development Installation
---------------------------------------

For development with all optional dependencies:

.. code-block:: shell

    pip install -e ".[dev]"

..

This installs:

* ``core-dev-tools>=1.0.1`` - Development tools
* ``core-tests>=2.0.3`` - Testing utilities
* ``pytest-xdist>=3.5.0`` - Parallel test execution

Quick Start
===============================================================================

Setting Up Environment
---------------------------------------

1. Install required libraries:

.. code-block:: shell

    pip install --upgrade pip
    pip install virtualenv

..

2. Create Python virtual environment:

.. code-block:: shell

    virtualenv --python=python3.12 .venv

..

3. Activate the virtual environment:

.. code-block:: shell

    source .venv/bin/activate

..

4. Install the package:

.. code-block:: shell

    pip install -e ".[dev]"

..

Basic Usage
---------------------------------------

Creating a Lambda Function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from aws_cdk import App, Environment
    from aws_cdk.aws_lambda import Code, Runtime
    from core_aws_cdk.stacks.lambdas import BaseLambdaStack

    app = App()
    stack = BaseLambdaStack(
        app,
        "MyLambdaStack",
        env=Environment(account="123456789", region="us-east-1")
    )

    stack.create_lambda(
        function_id="MyFunction",
        handler="index.handler",
        code=Code.from_asset("./lambda"),
        runtime=Runtime.PYTHON_3_12,
        function_name="my-function"
    )

    app.synth()

..

Creating S3 Bucket
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from core_aws_cdk.stacks.s3 import BaseS3Stack

    stack = BaseS3Stack(app, "MyS3Stack")

    bucket = stack.create_bucket(
        bucket_id="MyBucket",
        bucket_name="my-unique-bucket-name",
        versioned=True
    )

..

Creating SNS Topic with SQS Subscription
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from core_aws_cdk.stacks.sns import BaseSnsStack
    from core_aws_cdk.stacks.sqs import BaseSqsStack
    from aws_cdk.aws_sns_subscriptions import SqsSubscription

    # Create topic
    sns_stack = BaseSnsStack(app, "MySnsStack")
    topic = sns_stack.create_sns_topic(
        topic_id="MyTopic",
        topic_name="my-topic"
    )

    # Create queue
    sqs_stack = BaseSqsStack(app, "MySqsStack")
    queue = sqs_stack.create_sqs_queue(
        queue_id="MyQueue",
        queue_name="my-queue",
        with_dlq=True,
        dlq_id="MyQueueDLQ"
    )

    # Subscribe queue to topic
    topic.add_subscription(SqsSubscription(queue))

..

Lambda ZIP Packaging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from core_aws_cdk.stacks.lambdas import ZipAssetCode
    import pathlib

    code = ZipAssetCode(
        project_directory=pathlib.Path("/path/to/project"),
        work_dir=pathlib.Path("/path/to/lambda"),
        includes=["handler.py", "__init__.py"],
        include_project_folders=["commons"],
        debug=True
    )

    stack.create_lambda(
        function_id="MyFunction",
        handler="handler.lambda_handler",
        code=code,
        runtime=Runtime.PYTHON_3_12
    )

..

Testing
===============================================================================

Test Structure
---------------------------------------

The project includes comprehensive test coverage:

.. code-block:: text

    tests/
    ├── functional/          # Functional tests (deploy to AWS)
    │   ├── test_lambda_creation.py
    │   └── test_sns_sqs_lambda_s3_integration.py
    └── unit/               # Unit tests (fast, isolated)

..

Running Tests
---------------------------------------

Sequential Execution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run all tests:

.. code-block:: shell

    python manager.py run-tests
    python manager.py run-tests --test-type integration
    python manager.py run-coverage

    # Having proper AWS credentials...
    python manager.py run-tests --test-type functional --pattern "*.py"

    # Or using `pytest`...
    pytest
..

Run specific test file:

.. code-block:: shell

    pytest tests/functional/test_lambda_creation.py

..

Run specific test:

.. code-block:: shell

    pytest tests/functional/test_lambda_creation.py::TestLambdaCreation::test_create_and_invoke_lambda_with_inline_code

..

Parallel Execution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install pytest-xdist:

.. code-block:: shell

    pip install pytest-xdist
    # or
    pip install -e ".[dev]"

..

Run tests in parallel using all CPUs:

.. code-block:: shell

    pytest -n auto

..

Run with specific number of workers:

.. code-block:: shell

    pytest -n 4  # Use 4 parallel workers

..

Run functional tests with limited parallelism (recommended):

.. code-block:: shell

    pytest tests/functional/ -n 2  # Avoid AWS rate limits

..

Test Markers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Filter tests by markers:

.. code-block:: shell

    # Run only unit tests
    pytest -m unit

    # Run only functional tests
    pytest -m functional

    # Run only integration tests
    pytest -m integration

    # Exclude slow tests
    pytest -m "not slow"

..

Available markers:

* ``unit`` - Unit tests (fast, no external dependencies)
* ``functional`` - Functional tests (deploy to AWS, slower)
* ``integration`` - Integration tests (multiple services)
* ``slow`` - Slow running tests

Functional Tests
---------------------------------------

**IMPORTANT:** Functional tests deploy real resources to AWS and may incur costs.

Prerequisites
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. AWS credentials configured:

.. code-block:: shell

    aws configure

..

2. CDK CLI installed:

.. code-block:: shell

    npm install -g aws-cdk

..

3. Required AWS permissions:

   * Lambda (create, invoke, delete)
   * S3 (create bucket, put/get objects, delete)
   * SNS (create topic, publish)
   * SQS (create queue, send/receive messages)
   * CloudFormation (create/update/delete stacks)
   * IAM (create roles and policies)

Running Functional Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sequential (safer for AWS rate limits):

.. code-block:: shell

    pytest tests/functional/ -v -s

..

Parallel (faster but may hit rate limits):

.. code-block:: shell

    pytest tests/functional/ -n 2 -v -s

..

Important Notes:

* Tests automatically clean up resources after completion
* Each test uses temporary directories and unique resource names
* Tests include 10-minute timeouts for deployment and cleanup
* All logs captured with DEBUG level for troubleshooting

Test Output Options
---------------------------------------

Verbose output:

.. code-block:: shell

    pytest -v   # Show test names
    pytest -vv  # Show more details

..

Show print statements:

.. code-block:: shell

    pytest -s  # Show stdout/stderr and logger output

..

Combine options:

.. code-block:: shell

    pytest tests/functional/ -n auto -v -s

..

Debugging
---------------------------------------

Show full traceback:

.. code-block:: shell

    pytest --tb=long

..

Run only failed tests:

.. code-block:: shell

    pytest --lf  # Last failed
    pytest --ff  # Failed first

..

Stop on first failure:

.. code-block:: shell

    pytest -x

..

Drop into debugger on failure:

.. code-block:: shell

    pytest --pdb

..

Code Coverage
---------------------------------------

Generate coverage report:

.. code-block:: shell

    pytest --cov=core_aws_cdk --cov-report=html

..

Run with coverage in parallel:

.. code-block:: shell

    pytest -n auto --cov=core_aws_cdk --cov-report=html

..

View HTML report:

.. code-block:: shell

    open htmlcov/index.html

..

Testing Lambda Packaging
---------------------------------------

Before deploying Lambda functions, you can test the ZIP packaging locally to verify
that all dependencies and files are correctly bundled.

Basic Package Testing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a test script to verify Lambda package creation:

.. code-block:: python

    # test.py
    from core_aws_cdk.stacks.lambdas import ZipAssetCode
    import pathlib

    result = ZipAssetCode(
        project_directory=pathlib.Path("/path/to/project"),
        work_dir=pathlib.Path("/path/to/lambda"),
        include_project_folders=["commons"],
        includes=["__init__.py", "handler.py", "docs"],
        debug=True
    )

    print(result.package_path.resolve())

..

Run the test script:

.. code-block:: shell

    python test.py

..

Expected output:

.. code-block:: text

    /path/to/project/.build/lambda_XXXXX.zip

..

Verifying Package Contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Inspect the generated ZIP file:

.. code-block:: shell

    unzip -l /path/to/project/.build/lambda_XXXXX.zip

..

The ZIP should contain:

* Your Lambda handler files (``handler.py``, ``__init__.py``)
* Project folders specified in ``include_project_folders`` (``commons/``)
* Additional files from ``includes`` (``docs/``)
* Python dependencies from ``requirements.txt`` (if present)

Package Testing Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Key parameters for ``ZipAssetCode``:

* ``project_directory``: Root directory of your project
* ``work_dir``: Directory containing Lambda handler code
* ``includes``: List of files/folders to include from work_dir
* ``include_project_folders``: List of folders from project root to include
* ``debug``: Enable verbose logging (default: False)

Troubleshooting Package Issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Issue: Missing dependencies in package
"""""""""""""""""""""""""""""""""""""""

**Solution:** Create ``requirements.txt`` in your Lambda directory:

.. code-block:: shell

    cd /path/to/lambda
    echo "requests>=2.28.0" > requirements.txt
    python test.py

..

Issue: Package too large
"""""""""""""""""""""""""""""""""""""""

**Solution:** Exclude unnecessary files:

.. code-block:: python

    result = ZipAssetCode(
        project_directory=pathlib.Path("/path/to/project"),
        work_dir=pathlib.Path("/path/to/lambda"),
        includes=["handler.py"],  # Only include necessary files
        include_project_folders=["commons"],
        debug=False  # Disable debug for smaller package
    )

..

Issue: Wrong Python version in package
"""""""""""""""""""""""""""""""""""""""

**Solution:** Ensure virtual environment matches Lambda runtime:

.. code-block:: shell

    virtualenv --python=python3.12 .venv
    source .venv/bin/activate
    python test.py

..

CI/CD Integration
===============================================================================

GitHub Actions Example
---------------------------------------

.. code-block:: yaml

    name: Tests

    on: [push, pull_request]

    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3

          - name: Set up Python
            uses: actions/setup-python@v4
            with:
              python-version: '3.12'

          - name: Install dependencies
            run: |
              pip install -e ".[dev]"

          - name: Run Unit Tests
            run: |
              pytest tests/unit/ -n auto --junitxml=junit-unit.xml

          - name: Run Functional Tests
            run: |
              pytest tests/functional/ -n 2 --junitxml=junit-functional.xml
            env:
              AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
              AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
              AWS_DEFAULT_REGION: us-east-1

..

GitLab CI Example
---------------------------------------

.. code-block:: yaml

    stages:
      - test

    unit-tests:
      stage: test
      image: python:3.12
      script:
        - pip install -e ".[dev]"
        - pytest tests/unit/ -n auto --junitxml=junit-unit.xml
      artifacts:
        reports:
          junit: junit-unit.xml

    functional-tests:
      stage: test
      image: python:3.12
      script:
        - pip install -e ".[dev]"
        - npm install -g aws-cdk
        - pytest tests/functional/ -n 2 --junitxml=junit-functional.xml
      artifacts:
        reports:
          junit: junit-functional.xml
      only:
        - main
        - merge_requests

..

Architecture Examples
===============================================================================

Complete SNS → SQS → Lambda → S3 Integration
--------------------------------------------

.. code-block:: python

    from aws_cdk import App, Environment, Duration, CfnOutput
    from aws_cdk.aws_lambda import Code, Runtime
    from aws_cdk.aws_lambda_event_sources import SqsEventSource
    from aws_cdk.aws_sns_subscriptions import SqsSubscription
    from core_aws_cdk.stacks.lambdas import BaseLambdaStack
    from core_aws_cdk.stacks.s3 import BaseS3Stack
    from core_aws_cdk.stacks.sns import BaseSnsStack
    from core_aws_cdk.stacks.sqs import BaseSqsStack

    class IntegratedStack(BaseSnsStack, BaseSqsStack,
                          BaseLambdaStack, BaseS3Stack):
        pass

    app = App()
    stack = IntegratedStack(
        app,
        "IntegratedStack",
        env=Environment(account="123456789", region="us-east-1")
    )

    # Create S3 bucket
    bucket = stack.create_bucket(
        bucket_id="DataBucket",
        bucket_name=None  # Auto-generate
    )

    # Create SQS queue with DLQ
    queue = stack.create_sqs_queue(
        queue_id="ProcessQueue",
        queue_name="process-queue",
        with_dlq=True,
        dlq_id="ProcessQueueDLQ",
        max_receive_count=3
    )

    # Create SNS topic
    topic = stack.create_sns_topic(
        topic_id="EventTopic",
        topic_name="event-topic"
    )

    # Subscribe queue to topic
    topic.add_subscription(SqsSubscription(queue))

    # Create Lambda processor
    lambda_function = stack.create_lambda(
        function_id="Processor",
        handler="handler.lambda_handler",
        code=Code.from_asset("./lambda"),
        runtime=Runtime.PYTHON_3_12,
        timeout=Duration.minutes(5),
        environment={"BUCKET_NAME": bucket.bucket_name}
    )

    # Configure SQS as Lambda trigger
    lambda_function.add_event_source(SqsEventSource(queue))

    # Grant permissions
    bucket.grant_write(lambda_function)

    # Export outputs
    CfnOutput(stack, "TopicArn", value=topic.topic_arn)
    CfnOutput(stack, "BucketName", value=bucket.bucket_name)

    app.synth()

..

Performance Tips
===============================================================================

1. **Use parallel execution for independent tests:**

   .. code-block:: shell

       pytest -n auto

   ..

2. **Run fast unit tests first during development:**

   .. code-block:: shell

       pytest tests/unit/ -n auto

   ..

3. **Run functional tests with limited parallelism:**

   .. code-block:: shell

       pytest tests/functional/ -n 2  # Avoid AWS rate limits

   ..

4. **Use markers to run specific test subsets:**

   .. code-block:: shell

       pytest -m "unit and not slow" -n auto

   ..

Troubleshooting
===============================================================================

Common Issues
---------------------------------------

Issue: "Too many open files"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution:** Reduce number of parallel workers

.. code-block:: shell

    pytest -n 2  # Instead of -n auto

..

Issue: AWS rate limiting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution:** Run functional tests sequentially or with limited parallelism

.. code-block:: shell

    pytest tests/functional/  # Sequential
    # or
    pytest tests/functional/ -n 2  # Limited parallelism

..

Issue: Tests hanging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution:** Check CDK CLI timeouts. Current timeout is 600s (10 minutes).

Issue: CDK version mismatch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution:** Ensure CDK CLI version matches library version

.. code-block:: shell

    npm install -g aws-cdk@latest
    cdk --version

..

Issue: Node.js version warning
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution:** Ensure Node.js v20 or v22 is installed and accessible

.. code-block:: shell

    node --version
    which node

..

Contributing
===============================================================================

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass: ``pytest -n auto``
5. Run linting: ``pylint core_aws_cdk``
6. Run security checks: ``bandit -r core_aws_cdk``
7. Submit a pull request

License
===============================================================================

This project is licensed under the MIT License. See the LICENSE file for details.

Links
===============================================================================

* **Documentation:** https://core-aws-cdk.readthedocs.io/en/latest/
* **Repository:** https://gitlab.com/bytecode-solutions/core/core-aws-cdk
* **Issues:** https://gitlab.com/bytecode-solutions/core/core-aws-cdk/-/issues
* **Changelog:** https://gitlab.com/bytecode-solutions/core/core-aws-cdk/-/blob/master/CHANGELOG.md
* **PyPI:** https://pypi.org/project/core-aws-cdk/

Support
===============================================================================

For questions or support, please open an issue on GitLab or contact the maintainers.

Authors
===============================================================================

* **Alejandro Cora González** - *Initial work* - alek.cora.glez@gmail.com
