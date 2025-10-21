# aind-data-transfer-lite

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
![Interrogate](https://img.shields.io/badge/interrogate-100.0%25-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=codecov)
![Python](https://img.shields.io/badge/python->=3.10-blue?logo=python)

## Getting Started

### Who is this for?

You want to upload data to AIND's Cloud Storage platform on AWS.

### Prerequisites

- Install [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Authentication for write permissions to aind-open-data bucket. Please reach to AIND Scientific Computing for access.

## Installation
Install directly from PyPI. We recommend installing into a virtual environment or conda environment.
```bash
pip install aind-data-transfer-lite
```

## Usage

### Example Python Script

```python
from pathlib import Path
import os
from aind_data_transfer_lite.models import JobSettings
from aind_data_transfer_lite.upload_data import UploadDataJob

# Assuming running from same directory as this README file
cwd = os.getcwd()
behavior_path = Path(cwd) / "tests" / "resources" / "behavior_data"
ecephys_path = Path(cwd) / "tests" / "resources" / "ecephys_data"
metadata_path = Path(cwd) / "tests" / "resources" / "metadata_dir"

modality_directories = {
  "behavior": behavior_path,
  "ecephys": ecephys_path
}

metadata_directory = metadata_path

job_settings = JobSettings(
  dry_run=True,
  modality_directories=modality_directories,
  metadata_directory=metadata_directory,
  s3_bucket="aind-open-data-dev"
)

job = UploadDataJob(job_settings=job_settings)
job.run_job()
```

### Example Command Line (Linux and MacOs)
```bash
python -m aind_data_transfer_lite.upload_data \
--metadata_directory "./tests/resources/metadata_dir" \
--modality_directories '{"behavior": "./tests/resources/behavior_data", "ecephys": "./tests/resources/ecephys_data"}' \
--dry_run "True"
```

### Example Command Line (PowerShell)
```bash
python -m aind_data_transfer_lite.upload_data `
--metadata_directory "./tests/resources/metadata_dir" `
--modality_directories '{\"behavior\": \"./tests/resources/behavior_data\", \"ecephys\": \"./tests/resources/ecephys_data\"}' `
--dry_run "True"
```

## Contributing

For code development, clone the repo and install as
```bash
pip install -e ".[dev]"
```

### Linters and testing

There are several libraries used to run linters, check documentation, and run tests.

- Please test your changes using the **coverage** library, which will run the tests and log a coverage report:

```bash
coverage run -m unittest discover && coverage report
```

- Use **interrogate** to check that modules, methods, etc. have been documented thoroughly:

```bash
interrogate .
```

- Use **flake8** to check that code is up to standards (no unused imports, etc.):
```bash
flake8 .
```

- Use **black** to automatically format the code into PEP standards:
```bash
black .
```

- Use **isort** to automatically sort import statements:
```bash
isort .
```

### Pull requests

For internal members, please create a branch. For external members, please fork the repository and open a pull request from the fork. We'll primarily use [Angular](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit) style for commit messages. Roughly, they should follow the pattern:
```text
<type>(<scope>): <short summary>
```

where scope (optional) describes the packages affected by the code changes and type (mandatory) is one of:

- **build**: Changes that affect build tools or external dependencies (example scopes: pyproject.toml, setup.py)
- **ci**: Changes to our CI configuration files and scripts (examples: .github/workflows/ci.yml)
- **docs**: Documentation only changes
- **feat**: A new feature
- **fix**: A bugfix
- **perf**: A code change that improves performance
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests

### Semantic Release

The table below, from [semantic release](https://github.com/semantic-release/semantic-release), shows which commit message gets you which release type when `semantic-release` runs (using the default configuration):

| Commit message                                                                                                                                                                                   | Release type                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| `fix(pencil): stop graphite breaking when too much pressure applied`                                                                                                                             | ~~Patch~~ Fix Release, Default release                                                                          |
| `feat(pencil): add 'graphiteWidth' option`                                                                                                                                                       | ~~Minor~~ Feature Release                                                                                       |
| `perf(pencil): remove graphiteWidth option`<br><br>`BREAKING CHANGE: The graphiteWidth option has been removed.`<br>`The default graphite width of 10mm is always used for performance reasons.` | ~~Major~~ Breaking Release <br /> (Note that the `BREAKING CHANGE: ` token must be in the footer of the commit) |
