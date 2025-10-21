# Brizz SDK

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Brizz observability SDK for AI applications.

## Installation

```bash
pip install brizz
# or
uv add brizz
# or
poetry add brizz
```

## Quick Start

```python
from brizz import Brizz

# Initialize
Brizz.initialize(
    api_key='your-brizzai-api-key',
    app_name='my-app',
)
```

> **Important**: Initialize Brizz before importing any libraries you want to instrument (e.g.,
> OpenAI). If using `dotenv`, use `from dotenv import load_dotenv; load_dotenv()` before importing `brizz`.

## PII Masking

Automatically protects sensitive data in traces:

```python
# Option 1: Enable default masking (simple)
Brizz.initialize(
    api_key='your-api-key',
    masking=True,  # Enables all built-in PII patterns
)

# Option 2: Custom masking configuration
from brizz import Brizz, MaskingConfig, SpanMaskingConfig, AttributesMaskingRule

Brizz.initialize(
    api_key='your-api-key',
    masking=MaskingConfig(
        span_masking=SpanMaskingConfig(
            rules=[
                AttributesMaskingRule(
                    attribute_pattern=r'gen_ai\.(prompt|completion)',
                    mode='partial',  # 'partial' or 'full'
                    patterns=[r'sk-[a-zA-Z0-9]{32}'],  # Custom regex patterns
                ),
            ],
        ),
    ),
)
```

**Built-in patterns**: emails, phone numbers, SSNs, credit cards, API keys, crypto addresses, and
more. Use `masking=True` for defaults or `MaskingConfig` for custom rules.

## Session Tracking

Group related operations and traces under a session context. All telemetry within the wrapped
function will include the session ID:

```python
from brizz import with_session_id, awith_session_id


async def process_user_workflow(chat_id):
    # All traces, events, and spans within this function
    # will be tagged with session-123
    response = await awith_session_id(chat_id, openai.chat.completions.create,
        model='gpt-4',
        messages=[{'role': 'user', 'content': 'Hello'}],
    )

    return response


# For synchronous functions
def sync_workflow(chat_id: str, data: dict):
    # Process data with session context
    return with_session_id(chat_id, processed_data, data)
```

## Event Examples

```python
from brizz import emit_event

emit_event('user.signup', {'user_id': '123', 'plan': 'pro'})
emit_event('user.payment', {'amount': 99, 'currency': 'USD'})
```

## Deployment Environment

Optionally specify the deployment environment for better filtering and organization:

```python
Brizz.initialize(
    api_key='your-api-key',
    app_name='my-app',
    environment='production',  # Optional: 'dev', 'staging', 'production', etc.
)
```

## Environment Variables

```bash
BRIZZ_API_KEY=your-api-key                  # Required
BRIZZ_BASE_URL=https://telemetry.brizz.dev  # Optional
BRIZZ_APP_NAME=my-app                       # Optional
BRIZZ_ENVIRONMENT=production                # Optional: deployment environment (dev, staging, production)
```
