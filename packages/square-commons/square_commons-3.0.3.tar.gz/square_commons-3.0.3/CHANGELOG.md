# changelog

## v3.0.3

- dependencies
    - create all and dev sections for pytest dependencies.

## v3.0.2

- remove setup.py and switch to pyproject.toml

## v3.0.1

- docs
    - add GNU license.
    - update setup.py classifiers, author name.
    - move changelog to different file.

## v3.0.0

- api_utils
    - **breaking_change** in make_request change base_url to url.
    - in make_request change endpoint to optional kwarg.
    - mark make_request_json_output as deprecated.
- dependencies
    - add Deprecated>=1.2.18.
- tests
    - update test cases to account for change base_url to url in make_request.

## v2.2.0

- api_utils
    - add make_request.

## v2.1.0

- config_reader
    - new optional parameter sample_file_path.

## v2.0.0

- api_utils
    - make_request_json_output have separate paramater for data and json.
    - new optional parameter auth.
- email
    - add send_email_using_mailgun

## v1.5.0

- new dependencies: pytest, pytest-mock.
- added pytest test cases.
- add github workflow for auto test on commit.

## v1.4.1

- update default param for same_site to strict in api_utils -> create_cookie.

## v1.4.0

- add api_utils -> create_cookie.

## v1.3.0

- update api_utils -> make_request_json_output to send files as well.

## v1.2.0

- added make_request_json_output in api_utils.

## v1.1.0

- added api_utils with get_api_output_in_standard_format.

## v1.0.0

- initial version with config reading methods.