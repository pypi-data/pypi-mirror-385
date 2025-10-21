"""Main job to upload data to s3."""

import json
import logging
import os
import platform
import subprocess
from contextlib import closing
from datetime import datetime, timedelta
from functools import cached_property
from time import time

import boto3
from aind_data_schema.core.metadata import (
    CORE_FILES,
    REQUIRED_FILE_SETS,
    create_metadata_json,
)
from aind_data_schema_models.data_name_patterns import build_data_name

from aind_data_transfer_lite.models import JobSettings

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


class UploadDataJob:
    """Class to handle uploading data."""

    def __init__(self, job_settings: JobSettings):
        """
        Initialize class with job settings
        Parameters
        ----------
        job_settings : JobSettings
        """
        self.job_settings = job_settings

    @cached_property
    def s3_prefix(self) -> str:
        """Builds s3_prefix based on data_description.json file."""
        with open(
            self.job_settings.metadata_directory / "data_description.json", "r"
        ) as f:
            data_description = json.load(f)

        subject_id = data_description["subject_id"]
        creation_time = datetime.fromisoformat(
            data_description["creation_time"].replace("Z", "+00:00")
        )
        s3_prefix = build_data_name(
            label=subject_id, creation_datetime=creation_time
        )
        return s3_prefix

    @property
    def s3_root_location(self) -> str:
        """Returns root location in S3"""
        return f"s3://{self.job_settings.s3_bucket}/{self.s3_prefix}"

    def _check_s3_location(self):
        """
        Checks that s3_location does not exist.

        Raises
        ------
        FileExistsError

        """

        logging.info("Checking S3 Location")

        bucket = self.job_settings.s3_bucket
        prefix = self.s3_prefix
        with closing(boto3.client("s3")) as s3_client:
            results = s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=1,
            )
        if results["KeyCount"] != 0:
            raise FileExistsError(
                f"{self.s3_root_location} already exists!"
                f" Please contact a data admin for help."
            )

    def _check_metadata_files(self):
        """Checks required metadata files are present."""

        logging.info("Checking metadata directory")

        metadata_file_names = os.listdir(self.job_settings.metadata_directory)
        metadata_files = [m.replace(".json", "") for m in metadata_file_names]
        unexpected_files = set(metadata_files).difference(CORE_FILES)
        if unexpected_files:
            raise Exception(
                f"Unexpected files found in metadata directory!"
                f" {unexpected_files}"
            )
        required_files = REQUIRED_FILE_SETS["subject"]
        required_files.append("subject")
        missing_files = set(required_files).difference(metadata_files)
        if missing_files:
            raise Exception(
                f"Required metadata files not found in metadata directory!"
                f" {missing_files}"
            )
        for metadata_file_name in metadata_file_names:
            with open(
                self.job_settings.metadata_directory / metadata_file_name, "r"
            ) as f:
                json.load(f)

    @staticmethod
    def _run_s3_sync_command(src_folder: str, s3_location: str, dry_run: bool):
        """
        Upload a folder using aws cli.
        Parameters
        ----------
        src_folder : str
        s3_location : str
        dry_run : bool

        """
        if platform.system() == "Windows":
            shell = True
        else:
            shell = False
        command = ["aws", "s3", "sync", src_folder, s3_location]
        if dry_run:
            command.append("--dryrun")
        subprocess.run(command, check=True, shell=shell)

    def _upload_directory_data(self):
        """Upload data task."""

        logging.info("Uploading Modality Data")
        for modality, path in self.job_settings.modality_directories.items():
            s3_location = f"{self.s3_root_location}/{modality}"
            src_folder = str(path)
            self._run_s3_sync_command(
                src_folder=src_folder,
                s3_location=s3_location,
                dry_run=self.job_settings.dry_run,
            )

        logging.info("Uploading metadata.nd.json")
        src_folder = f"{self.job_settings.metadata_directory}"
        self._run_s3_sync_command(
            src_folder=src_folder,
            s3_location=self.s3_root_location,
            dry_run=self.job_settings.dry_run,
        )

    def _upload_metadata_nd_file(self):
        """Upload metadata.nd.json file to s3 location."""
        metadata_file_names = os.listdir(self.job_settings.metadata_directory)
        core_jsons = dict()
        for metadata_file in metadata_file_names:
            core_file_name = metadata_file.replace(".json", "")
            with open(
                self.job_settings.metadata_directory / metadata_file, "r"
            ) as f:
                file_contents = json.load(f)
            core_jsons[core_file_name] = file_contents
        metadata_nd = create_metadata_json(
            name=self.s3_prefix,
            location=self.s3_root_location,
            core_jsons=core_jsons,
        )
        object_key = f"{self.s3_prefix}/metadata.nd.json"
        contents = json.dumps(
            metadata_nd,
            indent=3,
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
        if self.job_settings.dry_run:
            logging.info(
                f"(dryrun) Uploading metadata.nd.json to"
                f" {self.s3_root_location}/metadata.nd.json"
            )
        else:
            logging.info(
                f"Uploading metadata.nd.json to"
                f" {self.s3_root_location}/metadata.nd.json"
            )
            with closing(boto3.client("s3")) as s3_client:
                s3_client.put_object(
                    Bucket=self.job_settings.s3_bucket,
                    Key=object_key,
                    Body=contents,
                )

    def run_job(self):
        """Run job entrypoint."""
        start_time = time()
        self._check_s3_location()
        self._check_metadata_files()
        self._upload_directory_data()
        self._upload_metadata_nd_file()
        end_time = time()
        time_delta = timedelta(seconds=int(end_time - start_time))
        logging.info(f"Job finished in {time_delta}.")


if __name__ == "__main__":

    main_job_settings = JobSettings()
    main_job = UploadDataJob(job_settings=main_job_settings)
    main_job.run_job()
