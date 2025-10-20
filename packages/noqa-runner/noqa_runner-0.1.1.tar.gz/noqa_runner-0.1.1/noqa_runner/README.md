# noqa-runner

AI-powered mobile test execution runner for iOS applications.

## Installation

```bash
pip install noqa-runner
```

## Quick Start

### CLI

```bash
# Run from command line
python -m noqa_runner run \
  --device-id "00008110-001234567890001E" \
  --build-path /path/to/app.ipa \
  --noqa-api-token $NOQA_API_TOKEN \
  --case-input-json '[
    {
      "case_instructions": "Open app and login with valid credentials"
    }
  ]'
```

**Options:**

```
--device-id TEXT              Device UDID for testing [required]
--build-path TEXT             Path to IPA build file [required]
--noqa-api-token TEXT         noqa API authentication token [required]
--case-input-json TEXT        JSON with test cases: [{case_instructions, test_id, case_name?}]
--app-context TEXT            Application context information [optional]
--agent-api-url TEXT          Agent API base URL [optional, default: https://agent.noqa.ai]
--log-level TEXT              Logging level [optional, default: INFO]
--appium-url TEXT             Appium server URL [optional, default: http://localhost:4723]
```

**Note:** Either `--case-input-json` or `--case-ids` must be provided. `bundle_id` is extracted automatically from the IPA file.

### Python API

```python
from uuid import uuid4
from noqa_runner.application.run_test_session import RunTestSession
from noqa_runner.domain.models.test_info import RunnerTestInfo

# Create session
session = RunTestSession()

# Run tests
results = session.run(
    device_id="00008110-001234567890001E",
    appium_url="http://localhost:4723",
    build_path="/path/to/app.ipa",
    noqa_api_token="your-token",
    tests=[
        RunnerTestInfo(
            test_id="...",
            case_instructions="Open app and verify home screen",
            case_name="Home Screen Test",
        )
    ],
)

for result in results:
    print(f"Test {result.case_name}: {result.status}")
```

## Logging

All logs are output in JSON format with the following fields:

```json
{
  "event": "test_started",
  "event_type": "progress",
  "test_id": "550e8400-e29b-41d4-a716-446655440000",
  "case_name": "Login Test",
  "timestamp": "2025-10-16T10:30:00Z"
}
```

Event types:
- `progress` - Test execution progress
- `result` - Final test result


## License

Proprietary - noqa.ai

## Support

For issues and questions, please contact sergey@noqa.ai
