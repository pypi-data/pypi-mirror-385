# Developing these tools

## Unit tests and linter

The unit tests and linter now use [Hatch](https://hatch.pypa.io/) and a
recent version of Python (as defined in `pyproject.toml` under `project.requires-python`).

**Available Hatch Commands:**

• **Testing:**

- `hatch run test:test` - Run unit tests with coverage
- `hatch run test:test tests/test_bootstrapper.py` - Run specific test files
- `hatch run test:test -k "test_metadata"` - Run tests with custom args
- `hatch run test:coverage-report` - Generate coverage report

• **Linting & Code Quality:**

- `hatch run lint:check` - Run all linting checks (ruff + mergify)
- `hatch run lint:fix` - Auto-fix ruff issues (formatting + import sorting)
- `hatch run lint:pkglint` - Package-level linting (build + twine check)

• **Type Checking:**

- `hatch run mypy:check` - Run mypy type checking

• **End-to-End Testing:**

- `hatch run e2e:setup-cov` - Setup coverage for subprocesses
- `hatch run e2e:run [command]` - Run any command in e2e environment
  - Example: `hatch run e2e:run ./e2e/test_build.sh`

**Note:** To skip coverage setup during local development (useful to avoid cluttering the working directory with coverage files), create a `.skip-coverage` file in the project root:

```bash
touch .skip-coverage
```

When this file exists, the e2e test scripts will skip coverage setup and display "Skipping coverage setup".

## Logging

Log messages should be all lower case.

When possible, log messages should be prefixed with the name of the distribution
being processed.

Information about long running processes should be logged using the "unit of
work" pattern. Each long step should be preceded and followed by log messages
writing to INFO level to show what is starting and stopping, respectively.

Detailed messages should be logged to DEBUG level so they will not appear on the
console by default.

## Building the project

The project uses [Hatch](https://hatch.pypa.io/) as its build system with [hatchling](https://hatch.pypa.io/latest/plugins/builder/wheel/) as the build backend. The build configuration is defined in `pyproject.toml`.

### Development installation

For development, you can install the project in editable mode:

```bash
# You can spawn a shell within an environment by using the hatch shell command.
# It installs the project in editable/development mode.
hatch shell

# Check if fromager is installed and available in the path
which fromager
```

Note: When a package is installed in editable/development mode, you can make changes to its source code directly. These changes are immediately reflected in your Python environment without needing to reinstall the package.

### Quick build

To build the project (both source distribution and wheel), use:

```bash
hatch build
```

This will create both `.tar.gz` (source distribution) and `.whl` (wheel) files in the `dist/` directory.

You can build specific formats by using `hatch build -t wheel` or `hatch build -t sdist`.

Alternatively, you can use the standard `build` module (which is included in the `[project.optional-dependencies.build]` section):

```bash
# Install build dependencies first
pip install build twine

# Build the project
python -m build
```

### Package validation

To validate the built packages, you can use the package linting script:

```bash
hatch run lint:pkglint
```

This command will:

1. Build the project using `python -m build`
2. Check the built packages with `twine check dist/*.tar.gz dist/*.whl`
3. Validate Python version consistency between `pyproject.toml` and GitHub Actions workflows

The validation will fail if:

- The package metadata is malformed
- Required files are missing from the distribution
- Python version requirements are inconsistent across configuration files

### Building documentation

- `hatch run docs:build` - Build Sphinx documentation
