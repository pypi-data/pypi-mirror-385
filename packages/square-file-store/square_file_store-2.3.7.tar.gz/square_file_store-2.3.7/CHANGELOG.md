# changelog

## v2.3.7

- dependencies
    - create all and dev sections for pytest dependencies.

## v2.3.6

- remove setup.py and switch to pyproject.toml

## v2.3.5

- env
    - SQUARE_LOGGER -> FORMATTER_CHOICE + ENABLE_REDACTION
- dependencies
    - square_logger>=3.0.0.

## v2.3.4

- move application logic to utils instead of routes.

## v2.3.3

- docs
    - move changelog to a new file.
    - update README.
    - switch to GNU General Public License v3.0.

## v2.3.2

- remove config.ini and config.testing.ini from version control.

## v2.3.1

- bump square_database_structure to >= 2.5.1
- switch to hard delete for files for db entries.

## v2.3.0

- env
    - add DB_IP, DB_PORT, DB_USERNAME, DB_PASSWORD
    - add ALLOW_ORIGINS
    - add config.testing.ini
    - file path reading through os.path.join method.
- testing
    - add conftest file to create and cleanup test database, also to patch config file.
    - add pytest.yaml to enable pytest in github actions.
    - update existing tests to use the new fixtures.
    - update get_patched_configuration and create_client_and_cleanup to be session scoped.

## v2.2.3

- bump square_logger to 2.0.0

## v2.2.2

- add auto logger decorator to all functions.
- add logs to errors in all endpoints.

## v2.2.1

- add rollback logic to upload_file/v0.

## v2.2.0

- setup auto docker image build github action.

## v2.1.0

- set allow_credentials=True.

## v2.0.0

- rearrange file structure.
- add versions to all api endpoints.
- standard output for json outputs.
- replace hardcoded column names with variables from square_database_structure.
- update tests.
- refactor some code logic.

## v1.0.1

- replace file_purpose with app_id.

## v1.0.0

- initial implementation.
