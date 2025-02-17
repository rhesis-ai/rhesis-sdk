# Rhesis SDK

<p align="center">
  <img src="https://cdn.prod.website-files.com/66f422128b6d0f3351ce41e3/66fd07dc0b6994070ec5b54b_Logo%20Rhesis%20Orange-p-500.png" alt="Rhesis Logo" width="300"/>
</p>

> Gen AI applications that deliver value, not surprises.

The Rhesis SDK enables developers to access curated test sets and generate dynamic ones for GenAI applications. It provides tools to tailor validations to your needs and integrate seamlessly to keep your Gen AI robust, reliable & compliant.

## Installation

Install the Rhesis SDK using pip:

```bash
pip install rhesis-sdk
```

## Getting Started

### 1. Obtain an API Key

1. Visit [https://app.rhesis.ai](https://app.rhesis.ai)
2. Sign up for a Rhesis account
3. Navigate to your account settings
4. Generate a new API key

Your API key will be in the format `rh-XXXXXXXXXXXXXXXXXXXX`. Keep this key secure and never share it publicly.

> **Note:** On the Rhesis App, you can also create test sets for your own use cases and access them via the SDK. You only need to connect your GitHub account to create a test set.

### 2. Configure the SDK

You can configure the Rhesis SDK either through environment variables or direct configuration:

#### Using Environment Variables

```bash
export RHESIS_API_KEY="your-api-key"
export RHESIS_BASE_URL="https://api.rhesis.ai"  # optional
```

#### Direct Configuration

```python
import rhesis 

# Set configuration directly
rhesis.base_url = "https://api.rhesis.ai"  # optional
rhesis.api_key = "rh-XXXXXXXXXXXXXXXXXXXX"
```

## Features

The Rhesis SDK currently provides functionality to work with Rhesis test sets through routine operations:

- **List Test Sets**: Browse through available curated test sets
- **Load Test Sets**: Load specific test sets for your use case
- **Download Test Sets**: Download test set data for offline use

## Quick Start

Before you start, you can configure the Rhesis SDK either through environment variables or direct configuration, as described above.

### Working with Test Sets

```python
from rhesis.entities import TestSet

# List all test sets
for test_set in TestSet().all():
    print(test_set)

# Load a specific test set
test_set = TestSet(id="agent-or-industry-fraud-harmful")
test_set.load()

# Download test set data
test_set.download()

```

For more detailed examples, check out our [example notebooks](examples/).

### Generating custom Test Sets

If none of the existing test sets fit your needs, you can generate your own.

You can check out [app.rhesis.ai](http://app.rhesis.ai). There you can define requirements, scenarios and personas, and even import your existing GitHub repository.

## About Rhesis AI

Rhesis AI helps organizations build Gen AI applications that deliver value, not surprises. Our platform enables you to:
- Access curated test sets
- Generate dynamic test sets
- Tailor validations to your specific needs
- Integrate testing seamlessly into your workflow
- Keep your Gen AI applications robust, reliable & compliant

Made in Potsdam, Germany 🇩🇪

Visit [rhesis.ai](https://rhesis.ai) to learn more about our platform and services.

## Community 💬

Join our [Discord server](https://discord.rhesis.ai) to connect with other users and developers.

## Hugging Face 🤗

You can also find us on [Hugging Face](https://huggingface.co/rhesis). There, you can find our test sets across multiple use cases.

## Support 🆘

For questions, issues, or feature requests:
- Visit our [documentation](https://docs.rhesis.ai)
- Contact us at support@rhesis.ai
- Create an issue in this repository

## License 📝

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.