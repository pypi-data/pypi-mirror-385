# -*- coding: utf-8 -*-

"""
AWS Lambda ZIP package builder with dependency 
management and optimization.
"""

import glob
import logging
import os
import pathlib
import shutil
import subprocess
import typing

from aws_cdk.aws_lambda import AssetCode
from core_mixins.logger import get_logger


class ZipAssetCode(AssetCode):  # pylint: disable=too-many-instance-attributes
    """
    It will produce the ZIP file which contains the package
    and the required dependencies...
    """

    # Default files and folders (commons) to include in the package...
    DEFAULT_INCLUDES = (
        "__init__.py",
        "handler.py",
        "main.py",
    )

    # Smart exclusions: Removes AWS-provided packages to reduce deployment size...
    DEFAULT_EXCLUDED_DEPENDENCIES = (
        "bin",
        "boto3",
        "botocore",
        "certifi",
        "charset_normalizer",
        "click",
        "coverage",
        "dateutil",
        "docutils",
        "idna",
        "jmespath",
        "packaging",
        "pip",
        "python-dateutil",
        "requests",
        "s3transfer",
        "setuptools",
        "urllib3",
    )

    DEFAULT_EXCLUDED_FILES = (
        "*.dist-debug",
        "__pycache__",
        "*.pyc",
        "*.pyo",
    )

    # Optional exclusions for compiled extensions that may not be needed
    # Only use if you're sure these aren't required by your dependencies
    OPTIONAL_EXCLUDED_BINARIES = (
        "_cffi_backend*.so",  # CFFI backend (if not using cryptography/cffi)
        "*.a",  # Static libraries
        "*.la",  # Libtool archives
    )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        project_directory: pathlib.Path,
        work_dir: pathlib.Path,
        includes: typing.Iterable[str] = DEFAULT_INCLUDES,
        include_project_folders: typing.Optional[typing.List[str]] = None,
        excluded_dependencies: typing.Iterable[str] = DEFAULT_EXCLUDED_DEPENDENCIES,
        excluded_files: typing.Iterable[str] = DEFAULT_EXCLUDED_FILES,
        python_version: str = "python3.12",
        pip_args: str = "",
        logger: typing.Optional[logging.Logger] = None,
        debug: bool = False,
    ) -> None:
        """
        Initialize ZipAssetCode for Lambda packaging.

        :param project_directory: Path to the folder where the project code lives.
        :param work_dir: Path to the folder where the Lambda code lives.
        :param includes: List of files and/or folders (within work_dir) to include
            in the package. Explicitly define which Lambda files and folders should
            be included in the ZIP. Examples: ["handler.py", "utils/", "config.json"]
        :param include_project_folders: List of folders (within project_directory) to include
            in the package. Useful whenever you need to include modules/files to the Lambda,
            but the code is common to other components and is located outside the Lambda folder.
        :param excluded_dependencies: Dependencies to exclude from the package.
            Use DEFAULT_EXCLUDED_DEPENDENCIES for standard AWS-provided packages.
        :param excluded_files: File patterns to exclude from package. Use DEFAULT_EXCLUDED_FILES
            for standard Python compiled files. To also exclude optional compiled binaries
            (like CFFI), combine with OPTIONAL_EXCLUDED_BINARIES.
        :param python_version: Python version used (default: "python3.12").
        :param pip_args: Extra arguments to pass to pip install command like
            "--implementation=cp --only-binary=:all: --platform=manylinux2010_x86_64"
        :param logger: Optional logger instance for custom logging.
        :param debug: Enable debug logging for verbose output.

        **Example basic usage:**

        .. code-block:: python

            code = ZipAssetCode(
                project_directory=pathlib.Path("/path/to/project"),
                work_dir=pathlib.Path("/path/to/lambda"),
                includes=["handler.py", "utils/"],
            )

        **Example with optional binary exclusions:**

        .. code-block:: python

            code = ZipAssetCode(
                project_directory=project_path,
                work_dir=lambda_path,
                includes=["handler.py", "utils/"],
                excluded_files=(
                    *ZipAssetCode.DEFAULT_EXCLUDED_FILES,
                    *ZipAssetCode.OPTIONAL_EXCLUDED_BINARIES
                ),
            )
        """

        self.work_dir = work_dir
        self.python_version = python_version
        self.project_directory = project_directory
        self.build_dir = self.work_dir / ".build"
        self.pip_args = pip_args
        self.debug = debug

        self._includes = includes
        self._include_project_folders = include_project_folders or []
        self._zip_file = work_dir.name

        self.excluded_dependencies = excluded_dependencies or []
        self.excluded_files = excluded_files or []

        if not logger:
            logger = get_logger(
                __name__,
                log_level=logging.DEBUG if self.debug else logging.INFO,
                reset_handlers=True,
                propagate=True)

        self.logger = logger
        if self.debug:
            self.logger.setLevel(logging.DEBUG)

        path = self.create_package()
        self.package_path: pathlib.Path = path

        # Calling `super` at the end on purpose...
        super().__init__(path.as_posix())

    @property
    def is_inline(self) -> bool:
        return False

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    # pylint: disable=logging-fstring-interpolation
    # pylint: disable=broad-exception-caught
    def create_package(self) -> pathlib.Path:
        """Create the Lambda deployment package as a ZIP file."""
        self.logger.debug("=" * 70)
        self.logger.debug("Starting Lambda package creation")
        self.logger.debug(f"Project folder: {self.project_directory}")
        self.logger.debug(f"Lambda folder: {self.work_dir}")
        self.logger.debug(f"Build folder: {self.build_dir}")
        self.logger.debug("=" * 70)

        try:
            os.chdir(self.work_dir.as_posix())
            self.logger.debug("Removing previous content from build folder...")
            shutil.rmtree(self.build_dir, ignore_errors=True)
            self.logger.debug("Creating build folder...")
            self.build_dir.mkdir(parents=True)

            # STEP 1: Install dependencies
            self.logger.debug("\n[STEP 1] Installing dependencies if required.")
            requirements_path = self.work_dir / "requirements.txt"
            if requirements_path.exists():
                self.logger.debug(f"Installing packages from: {requirements_path}")

                # Build pip command
                pip_cmd = [
                    self.python_version, "-m", "pip", "install",
                    "--target", str(self.build_dir),
                    "--requirement", str(requirements_path)
                ]

                # Add extra pip arguments if provided
                if self.pip_args:
                    pip_cmd.extend(self.pip_args.split())

                self.logger.debug(f"Running: {' '.join(pip_cmd)}")
                subprocess.run(pip_cmd, check=True, capture_output=not self.debug)

                # Strip .so files to reduce size
                self.logger.debug("Stripping shared library files...")
                for so_file in self.build_dir.rglob("*.so"):
                    try:
                        subprocess.run(["strip", str(so_file)], check=False, capture_output=True)
                    except Exception as e:
                        self.logger.debug(f"Could not strip {so_file}: {e}")

            # STEP 2: Remove excluded elements
            self.logger.debug("\n[STEP 2] Removing excluded elements.")
            excluded_dependencies = set(self.excluded_dependencies)
            excluded_files = set(self.excluded_files)

            for pattern in excluded_dependencies.union(excluded_files):
                pattern = str(self.build_dir / '**' / pattern)
                self.logger.debug(f"Searching for pattern: {pattern}")
                files = glob.glob(pattern, recursive=True)

                for file_path in files:
                    try:
                        if os.path.isdir(file_path):
                            self.logger.debug(f"Removing directory: {file_path}")
                            shutil.rmtree(file_path)
                        elif os.path.isfile(file_path):
                            self.logger.debug(f"Removing file: {file_path}")
                            os.remove(file_path)

                    except OSError as e:
                        self.logger.warning(f"Error deleting file/folder: {file_path} - {e}")

            # STEP 3: Copy project files
            self.logger.debug("\n[STEP 3] Copying project files")

            for folder in self._include_project_folders:
                folder_path = (self.project_directory / folder).resolve()
                dest_path = self.build_dir / folder_path.name

                self.logger.debug(f"Copying project folder: {folder_path}")
                if folder_path.is_dir():
                    shutil.copytree(folder_path, dest_path, dirs_exist_ok=True)

                else:
                    shutil.copy2(folder_path, dest_path)

            if self._includes:
                for include in self._includes:
                    src_path = (pathlib.Path.cwd() / include).resolve()
                    dest_path = self.build_dir / src_path.name

                    self.logger.debug(f"Copying: {src_path}...")
                    if src_path.is_dir():
                        shutil.copytree(src_path, dest_path, dirs_exist_ok=True)

                    else:
                        shutil.copy2(src_path, dest_path)

            # STEP 4: Create ZIP package
            self.logger.debug("\n[STEP 4] Creating ZIP package")
            zip_file_path = (self.work_dir / self._zip_file).resolve()
            self.logger.debug(f"Creating package: {zip_file_path}.zip")

            shutil.make_archive(
                base_name=str(zip_file_path),
                format="zip",
                root_dir=str(self.build_dir),
                verbose=self.debug
            )

            final_path = self.work_dir.joinpath(self._zip_file + ".zip").resolve()
            self.logger.debug(f"Package created successfully: {final_path}")
            return final_path

        except Exception as ex:
            self.logger.error(f"Error during build: {ex}")
            raise RuntimeError(f"Error during build: {ex}") from ex
