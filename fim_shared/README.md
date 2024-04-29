# FIM Shared Library

This library contains shared code that is used across the FIM project. It is built as a poetry package
and is used as a dependency in the Inventory and IAM microservices.

## Making Updates

Updates can be made to the FIM package like any other python code. However, once updates are made you should follow these steps:

1. Update the version listed in the `pyproject.toml` file
2. Run `poetry build` to build the package
3. Copy the new `.tar.gz` file in the `dist` folder to the services that need the updates
4. Update the version reference in updated services' `pyproject.toml` file
5. Run `poetry update fim` from within the respective service to update the dependency
