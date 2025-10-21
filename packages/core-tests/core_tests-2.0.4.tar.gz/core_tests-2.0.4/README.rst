core-tests
===============================================================================

This project contains basic elements for testing purposes and the ability 
to run (via console commands) tests and code coverage (unittest-based). This way, we can 
stick to the `DRY -- Don't Repeat Yourself` principle and avoid code duplication
in each python project where tests coverage and tests execution are
expected...

===============================================================================

.. image:: https://img.shields.io/pypi/pyversions/core-tests.svg
    :target: https://pypi.org/project/core-tests/
    :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-tests/-/blob/main/LICENSE
    :alt: License

.. image:: https://gitlab.com/bytecode-solutions/core/core-tests/badges/release/pipeline.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-tests/-/pipelines
    :alt: Pipeline Status

.. image:: https://readthedocs.org/projects/core-tests/badge/?version=latest
    :target: https://readthedocs.org/projects/core-tests/
    :alt: Docs Status

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
    :alt: Security

|


Installation
===============================================================================

Install from PyPI using pip:

.. code-block:: bash

    pip install core-tests

Or using uv:

.. code-block:: bash

    uv pip install core-tests


Features
===============================================================================

* **Dual Test Engine Support**: Run tests using either `unittest` or `pytest` frameworks
* **Flexible Test Discovery**: Supports multiple file patterns:
    - `test_*.py` (standard pattern)
    - `*_test.py` (alternative pattern)
    - `tests_*.py` (custom pattern)
* **Custom Pattern Support**: Specify custom file patterns using the `--pattern` flag
* **Test Organization**: Run tests by type (unit, integration, functional, etc.)
* **Coverage Reports**: Generate coverage reports with both frameworks
* **CLI Integration**: Easy integration via Click command collections


How to Use
===============================================================================

Create a ``manager.py`` file in your project root to integrate 
the test commands:

.. code-block:: python

    # manager.py
    from click.core import CommandCollection
    from core_tests.tests.runner import cli_tests

    if __name__ == "__main__":
        cli = CommandCollection(sources=[cli_tests()])
        cli()

This setup provides two commands:

* ``run-tests``: Execute test suites with unittest or pytest
* ``run-coverage``: Generate code coverage reports

Example usage:

.. code-block:: bash

    python manager.py run-tests --test-type unit
    python manager.py run-coverage --engine pytest


Available Commands
===============================================================================

run-tests
-------------------------------------------------------------------------------

Execute test suites with flexible options:

**Options:**

* ``--engine``: Test engine to use (``unittest`` or ``pytest``). Default: ``unittest``
* ``--test-type``: Folder name under ``./tests`` directory (e.g., ``unit``, ``integration``, ``functional``)
* ``--pattern``: File pattern to match test files (e.g., ``*.py``, ``test_*.py``). Works with both engines.

**Examples:**

.. code-block:: bash

    # Run unit tests with unittest (default)
    python manager.py run-tests --test-type unit

    # Run integration tests with pytest
    python manager.py run-tests --engine pytest --test-type integration

    # Run tests with custom pattern
    python manager.py run-tests --test-type functional --pattern "test_*.py"

    # Run all tests in a custom folder
    python manager.py run-tests --test-type "custom_folder"


run-coverage
-------------------------------------------------------------------------------

Generate code coverage reports:

**Options:**

* ``--engine``: Test engine to use (``unittest`` or ``pytest``). Default: ``unittest``

**Examples:**

.. code-block:: bash

    # Generate coverage with unittest
    python manager.py run-coverage

    # Generate coverage with pytest
    python manager.py run-coverage --engine pytest


Quick Start
===============================================================================

Setting Up Environment
-------------------------------------------------------------------------------

1. Install required libraries:

.. code-block:: bash

    pip install --upgrade pip
    pip install virtualenv

2. Create Python virtual environment:

.. code-block:: bash

    virtualenv --python=python3.12 .venv

3. Activate the virtual environment:

.. code-block:: bash

    source .venv/bin/activate

4. Install the package:

.. code-block:: bash

    pip install -e ".[dev]"


Tests and Coverage
-------------------------------------------------------------------------------

.. code-block:: bash

    python manager.py run-tests --test-type unit
    python manager.py run-tests --test-type integration
    python manager.py run-tests --test-type "another folder that contains test cases under ./tests"
    python manager.py run-tests --test-type functional --pattern "*.py"


Using PyTest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The `unittest` framework cannot discover or run pytest-style tests, it is designed to
discover and run tests that are subclasses of `unittest.TestCase` and follow its
conventions. Pytest-style tests (i.e., functions named test_* that are not inside a
`unittest.TestCase` class, or tests using pytest fixtures, parametrize, etc.) are not
recognized by unittest's discovery mechanism, `unittest` will simply ignore standalone
test functions and any pytest-specific features...

That's why you can use PyTest if required.

.. code-block:: bash

    python manager.py run-tests --engine pytest

..

Test coverage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    python manager.py run-coverage                          # For `unittest` framework...
    python manager.py run-coverage --engine pytest          # For `PyTest`...
    pytest -n auto --cov=core_tests --cov-report=html       # Direct `pytest` execution...

..


Best Practices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When working with pytest, consider these optimization strategies:

1. **Use parallel execution for independent tests:**

   .. code-block:: bash

       pytest -n auto

   ..

2. **Run fast unit tests first during development:**

   .. code-block:: bash

       pytest tests/unit/ -n auto

   ..

3. **Run functional tests with limited parallelism:**

   .. code-block:: bash

       pytest tests/functional/ -n 2  # Avoid AWS rate limits

   ..

4. **Use markers to run specific test subsets:**

   .. code-block:: bash

       pytest -m "unit and not slow" -n auto

   ..


Contributing
===============================================================================

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass: ``pytest -n auto``
5. Run linting: ``pylint core_tests``
6. Run security checks: ``bandit -r core_tests``
7. Submit a pull request


License
===============================================================================

This project is licensed under the MIT License. See the LICENSE file for details.


Links
===============================================================================

* **Documentation:** https://core-tests.readthedocs.io/en/latest/
* **Repository:** https://gitlab.com/bytecode-solutions/core/core-tests
* **Issues:** https://gitlab.com/bytecode-solutions/core/core-tests/-/issues
* **Changelog:** https://gitlab.com/bytecode-solutions/core/core-tests/-/blob/master/CHANGELOG.md
* **PyPI:** https://pypi.org/project/core-tests/


Support
===============================================================================

For questions or support, please open an issue on GitLab or contact the maintainers.


Authors
===============================================================================

* **Alejandro Cora González** - *Initial work* - alek.cora.glez@gmail.com
