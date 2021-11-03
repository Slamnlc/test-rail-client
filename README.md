## testrail-api-client ##

testrail-api-client - is a client for provide integration with TestRail

General information about [TestRail Api](https://www.gurock.com/testrail/docs/api)

**Requirements**

- requests
- pytest
- gherkin-official
- pytest-bdd

**Installation**

```shell
pip install pytest-testrail-api-client
```

**Configuration**
Starting from version 0.3 you can configure testrail client credentials with 3 way:

Way 1. Directly set credentials in class constructor

```shell
from pytest_testrail_api_client.test_rail import TestRail
test_rail = TestRail('your_host', 'your_username', 'your_token')
```

Way 2. Set credentials in pytest.ini or in test_rail.ini This files must be in root folder project path Add
group [pytest]
Add variables:

- **testrail-email**
- **testrail-key**
- **testrail-url**

Example **pytest.ini** or **test_rail.ini**

```shell
[saucelab]
testrail-email = your_email
testrail-key = your_token
testrail-url = your_host
```

When you add credentials to ini file:

```shell
from pytest_testrail_api_client.test_rail import TestRail
test_rail = TestRail()
```

Way 3. You can set environment variables:

- TESTRAIL_EMAIL
- TESTRAIL_KEY
- TESTRAIL_URL

When you add credentials to environment variables:

```shell
from pytest_testrail_api_client.test_rail import TestRail
test_rail = TestRail()
```

**Features in version: 0.3.1**

- Access to TestRail Api
- Export feature files to TestRail (use pytest --pytest_testrail_export_test_cases
  --pytest-testrail-feature-files-relative-path "%RELATIVE_PATH%")
- Export tests results to TestRail (use pytest --pytest-testrail-export-test-results --pytest-testrail-test-plan-id
  %PLAN_ID% --pytest-testrail-test-configuration-name %CONFIGURATION%)
- Scenarios validation (please, see pytest_testrail_api_client/client_config.py)
- Tags replacing (for example: you have automation status "To Be Automated" and you use tag "to_automate" if feactures
  you can set it in variable REPLACE_TAGS - it will bind these tags)
- Priority replace: variable PRIORITY_REPLACE

**Usage examples**

```shell
from pytest_testrail_api_client.test_rail import TestRail
test_rail = TestRail()
case = test_rail.cases.get_case(1)
```
