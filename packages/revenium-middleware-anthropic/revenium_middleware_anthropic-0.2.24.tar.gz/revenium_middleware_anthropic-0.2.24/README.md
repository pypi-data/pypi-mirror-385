#  Revenium Middleware for Anthropic

[![PyPI version](https://img.shields.io/pypi/v/revenium-middleware-anthropic.svg)](https://pypi.org/project/revenium-middleware-anthropic/)
[![Python Versions](https://img.shields.io/pypi/pyversions/revenium-middleware-anthropic.svg)](https://pypi.org/project/revenium-middleware-anthropic/)
[![Documentation](https://img.shields.io/badge/docs-revenium.io-blue)](https://docs.revenium.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready middleware library for metering and monitoring Anthropic API usage in Python applications. Supports both direct Anthropic API and AWS Bedrock with comprehensive streaming functionality. 🐍✨

## 📊 Features

- **📊 Precise Usage Tracking**: Monitor tokens, costs, and request counts for Anthropic chat completions
- **🔌 Seamless Integration**: Drop-in middleware that works with minimal code changes
- **☁️ AWS Bedrock Support**: Full integration with automatic detection and metering for Anthropic models via AWS Bedrock
- **🌊 Complete Streaming Support**: Full streaming functionality for both Anthropic API and AWS Bedrock
- **🔧 Hybrid Initialization**: Auto-initialization on import + explicit control for advanced configuration
- **⚡ Thread-Safe**: Production-ready with comprehensive thread safety for concurrent applications
- **⚙️ Flexible Configuration**: Customize metering behavior to suit your application needs

## 🎯 What's Supported

| Feature | Direct Anthropic API | AWS Bedrock |
|---------|---------------------|-------------|
| **Chat Completion** | ✅ Full support | ✅ Full support |
| **Streaming** | ✅ Full support | ✅ Full support |
| **Token Metering** | ✅ Automatic | ✅ Automatic |
| **Metadata Tracking** | ✅ Full support | ✅ Full support |
| **Thread Safety** | ✅ Production-ready | ✅ Production-ready |
| **Auto-initialization** | ✅ Zero-config | ✅ Zero-config |

**Note**: The middleware only wraps `messages.create` and `messages.stream` endpoints. Other Anthropic SDK features work normally but aren't metered.

## 📥 Installation

```bash
# Basic installation
pip install revenium-middleware-anthropic

# With AWS Bedrock support
pip install revenium-middleware-anthropic[bedrock]
```

## 🚀 Quick Start

### Zero-Config Integration

Simply set your environment variables and import the middleware. Your Anthropic calls will be metered automatically:

```python
import anthropic
import revenium_middleware_anthropic  # Auto-initializes on import

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "What is the meaning of life, the universe and everything?"
        }
    ]
)
print(message.content[0].text)
```

The middleware automatically intercepts Anthropic API calls and sends metering data to Revenium without requiring any changes to your existing code.

### 🔧 Hybrid Initialization

The middleware supports both automatic and explicit initialization:

```python
import revenium_middleware_anthropic

# Option 1: Auto-initialization (recommended for most users)
# Just import and use - middleware activates automatically

# Option 2: Explicit control (for advanced configuration)
if not revenium_middleware_anthropic.is_initialized():
    success = revenium_middleware_anthropic.initialize()
    if not success:
        print("Configuration needed")
```

### Enhanced Tracking with Metadata

For more granular usage tracking and detailed reporting, add the `usage_metadata` parameter:

```python
import anthropic
import revenium_middleware_anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Explain machine learning briefly."
        }
    ],
    usage_metadata={
         "trace_id": "conv-28a7e9d4",
         "task_type": "summarize-customer-issue",
         "subscriber": {
             "id": "subscriberid-1234567890",
             "email": "user@example.com",
             "credential": {
                 "name": "engineering-api-key",
                 "value": "sk-ant-api03-..."
             }
         },
         "organization_id": "acme-corp",
         "agent": "support-agent",
    }
)
print(message.content[0].text)
```

## ☁️ AWS Bedrock Integration

This middleware provides complete AWS Bedrock integration with automatic detection and full streaming support, enabling you to meter token usage while routing requests through Amazon's infrastructure.

### 📦 Installation for Bedrock

To use AWS Bedrock integration, install with the `bedrock` extra:

```bash
pip install revenium-middleware-anthropic[bedrock]
```

### 🔍 Automatic Provider Detection

The middleware automatically chooses between Bedrock and direct Anthropic API:

| Detection Method | When Used | Example |
|-----------------|-----------|---------|
| **AWS Credentials** | When AWS credentials are configured and accessible | `aws configure` or IAM roles |
| **Base URL Detection** | When `base_url` contains `amazonaws.com` | Custom Bedrock endpoints |
| **Environment Variables** | When AWS environment variables are set | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| **Default** | When none of the above apply | Standard Anthropic API |

**Key Point**: The middleware defaults to direct Anthropic API for safety. Bedrock is only used when explicitly configured or detected.

### 💡 Quick Start Examples

#### Basic Usage (Direct Anthropic API)
```python
import anthropic
import revenium_middleware_anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-haiku-20240307",
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=50
)
# Automatically metered with provider="ANTHROPIC"
```

#### AWS Bedrock (Automatic Detection)
```python
# Configure AWS credentials first (aws configure, IAM roles, etc.)
import anthropic
import revenium_middleware_anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-haiku-20240307",  # Auto-maps to Bedrock model
    messages=[{"role": "user", "content": "Hello from Bedrock!"}],
    max_tokens=50
)
# Automatically metered with provider="AWS" when Bedrock is detected
```

#### Bedrock with Explicit Base URL
```python
import anthropic
import revenium_middleware_anthropic

# Force Bedrock by specifying base_url
client = anthropic.Anthropic(
    base_url="https://bedrock-runtime.us-east-1.amazonaws.com"
)
response = client.messages.create(
    model="claude-3-haiku-20240307",
    messages=[{"role": "user", "content": "What is AWS Bedrock?"}],
    max_tokens=100
)
# Guaranteed to use Bedrock with provider="AWS"
```

**💡 See the `examples/` directory for comprehensive examples:**
- `examples/anthropic-basic.py` - Simple zero-config usage (direct Anthropic API)
- `examples/anthropic-advanced.py` - Production-ready with metadata (direct Anthropic API)
- `examples/anthropic-streaming.py` - Streaming functionality (direct Anthropic API)
- `examples/anthropic-bedrock.py` - Complete AWS Bedrock integration (all examples via Bedrock)

### ⚙️ Configuration

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REVENIUM_METERING_API_KEY` | Your Revenium API key | **Required** |
| `REVENIUM_METERING_BASE_URL` | Revenium API endpoint | **Required** |
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `REVENIUM_BEDROCK_DISABLE` | Set to `1` to disable Bedrock support | Not set |

#### AWS Authentication

The middleware uses the standard AWS credential chain:

1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS credentials file (`~/.aws/credentials`)
3. IAM roles (for EC2/Lambda/ECS)
4. AWS SSO

**Required AWS permissions:**
- `bedrock:InvokeModel` (for non-streaming requests)
- `bedrock:InvokeModelWithResponseStream` (for streaming requests)

### 📋 Supported Models

The middleware automatically maps Anthropic model names to Bedrock model IDs:

| Anthropic Model | Bedrock Model ID |
|----------------|------------------|
| `claude-3-opus-20240229` | `anthropic.claude-3-opus-20240229-v1:0` |
| `claude-3-sonnet-20240229` | `anthropic.claude-3-sonnet-20240229-v1:0` |
| `claude-3-haiku-20240307` | `us.anthropic.claude-3-5-haiku-20241022-v1:0` |
| `claude-3-5-sonnet-20240620` | `anthropic.claude-3-5-sonnet-20240620-v1:0` |
| `claude-3-5-sonnet-20241022` | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `claude-3-5-haiku-20241022` | `anthropic.claude-3-5-haiku-20241022-v1:0` |

For other models, the middleware uses the format `anthropic.{model_name}`.

## 🌊 Streaming Support

The middleware provides complete streaming support for both direct Anthropic API and AWS Bedrock with identical interfaces and automatic provider detection.

### Features

- **Universal Interface**: Same code works with both Anthropic API and AWS Bedrock
- **Automatic Detection**: Provider routing happens transparently
- **Complete Token Tracking**: Accurate token counting and metering for streaming responses
- **Thread-Safe**: Production-ready concurrent streaming support
- **Graceful Fallback**: Automatic fallback to direct API if Bedrock streaming fails

### Basic Streaming Example

```python
import anthropic
import revenium_middleware_anthropic

client = anthropic.Anthropic()  # Auto-detects provider

# Streaming works identically with both providers
with client.messages.stream(
    model="claude-3-haiku-20240307",
    messages=[{"role": "user", "content": "Count from 1 to 5"}],
    max_tokens=50,
    usage_metadata={
        "trace_id": "streaming-demo-001",
        "task_type": "streaming-chat",
        "organization_id": "my-org"
    }
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Get final usage information
final_message = stream.get_final_message()
print(f"\nTokens: {final_message.usage.input_tokens} + {final_message.usage.output_tokens}")
```

### Bedrock Streaming Example

```python
import anthropic
import revenium_middleware_anthropic

# Force Bedrock by specifying base_url
client = anthropic.Anthropic(
    base_url="https://bedrock-runtime.us-east-1.amazonaws.com"
)

with client.messages.stream(
    model="claude-3-haiku-20240307",
    messages=[{"role": "user", "content": "Write a haiku about streaming data"}],
    max_tokens=100,
    usage_metadata={
        "trace_id": "bedrock-stream-001",
        "task_type": "bedrock-streaming",
        "organization_id": "aws-demo"
    }
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print("\n✅ Bedrock streaming completed with automatic token metering!")
```

View the [examples](https://github.com/revenium/revenium-middleware-anthropic-python/tree/main/examples) directory for more code samples for both streaming and non-streaming AI calls.

## 🏷️ Metadata Fields

The `usage_metadata` parameter supports the following fields for detailed tracking:

| Field                        | Description                                               | Use Case                                                          |
|------------------------------|-----------------------------------------------------------|-------------------------------------------------------------------|
| `trace_id`                   | Unique identifier for a conversation or session           | Group multi-turn conversations for performance & cost tracking                           |
| `task_type`                  | Classification of the AI operation by type of work        | Track cost & performance by purpose (e.g., classification, summarization)                                  |
| `subscriber`                 | Object containing subscriber information                   | Track cost & performance by individual users and their credentials                                          |
| `subscriber.id`              | The id of the subscriber from non-Revenium systems        | Track cost & performance by individual users (if customers are anonymous or tracking by emails is not desired)   |
| `subscriber.email`           | The email address of the subscriber                       | Track cost & performance by individual users (if customer e-mail addresses are known)                      |
| `subscriber.credential`      | Object containing credential information                   | Track cost & performance by API keys and credentials                                                       |
| `subscriber.credential.name` | An alias for an API key used by one or more users         | Track cost & performance by individual API keys                                                            |
| `subscriber.credential.value`| The key value associated with the subscriber (i.e an API key)     | Track cost & performance by API key value (normally used when the only identifier for a user is an API key) |
| `organization_id`            | Customer or department ID from non-Revenium systems       | Track cost & performance by customers or business units                                                    |
| `subscription_id`            | Reference to a billing plan in non-Revenium systems       | Track cost & performance by a specific subscription                                                        |
| `product_id`                 | Your product or feature making the AI call                | Track cost & performance across different products                                                         |
| `agent`                      | Identifier for the specific AI agent                      | Track cost & performance by AI agent                                                           |
| `response_quality_score`     | The quality of the AI response (0..1)                     | Track AI response quality                                                                                  |

**All metadata fields are optional**. Adding them enables more detailed reporting and analytics in Revenium.

## 📚 Examples

The `examples/` directory contains practical demonstrations of all middleware features:

| Example | Description | Key Features |
|---------|-------------|--------------|
| **`anthropic-basic.py`** | Zero-config setup | Auto-initialization, basic metering (direct API) |
| **`anthropic-advanced.py`** | Production template | Custom metadata, detailed tracking (direct API) |
| **`anthropic-streaming.py`** | Streaming responses | Real-time streaming, token tracking (direct API) |
| **`anthropic-bedrock.py`** | AWS Bedrock integration | All features via Bedrock: chat, metadata, streaming |

Each example includes:
- ✅ **Working code** that you can run immediately
- ✅ **Environment setup** with `.env` file loading
- ✅ **Error handling** and graceful fallbacks
- ✅ **Detailed output** showing what gets tracked
- ✅ **Comments** explaining key concepts

**Quick start**: `python examples/anthropic-basic.py`

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"No module named 'boto3'"** | Install with Bedrock support: `pip install revenium-middleware-anthropic[bedrock]` |
| **Requests go to Anthropic instead of Bedrock** | Verify AWS credentials: `aws sts get-caller-identity` |
| **"AccessDenied" errors** | Ensure AWS credentials have `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` permissions |
| **Model not available** | Check if Claude models are available in your AWS region |
| **Middleware not working** | Verify `REVENIUM_METERING_API_KEY` and `REVENIUM_METERING_BASE_URL` are set |
| **Streaming errors** | Check AWS credentials; middleware automatically falls back to direct API |

### Debug Mode

Enable debug logging to see provider detection and routing decisions:

```bash
export REVENIUM_LOG_LEVEL=DEBUG
python your_script.py
```

### Force Direct Anthropic API

To disable Bedrock detection temporarily:

```bash
export REVENIUM_BEDROCK_DISABLE=1
python your_script.py
```

### Check Initialization Status

```python
import revenium_middleware_anthropic

if revenium_middleware_anthropic.is_initialized():
    print("✅ Middleware is ready")
else:
    print("⚠️ Middleware needs configuration")
```

## 📋 Compatibility

- 🐍 **Python 3.8+**
- 🤖 **Anthropic Python SDK** (latest version recommended)
- ☁️ **AWS Bedrock** (with `boto3>=1.34.0` when using `[bedrock]` extra)
- ⚡ **Thread-Safe** (production-ready for concurrent applications)

## 🔍 Logging

Control logging with the `REVENIUM_LOG_LEVEL` environment variable:

```bash
# Enable debug logging
export REVENIUM_LOG_LEVEL=DEBUG
python your_script.py

# Or inline
REVENIUM_LOG_LEVEL=DEBUG python your_script.py
```

**Available log levels:**
- `DEBUG`: Detailed debugging information (provider detection, routing decisions)
- `INFO`: General information (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only

## Contributing

See [CONTRIBUTING.md](https://github.com/revenium/revenium-middleware-anthropic-python/blob/main/CONTRIBUTING.md)

## Security

See [SECURITY.md](https://github.com/revenium/revenium-middleware-anthropic-python/blob/main/SECURITY.md)

##  License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/revenium/revenium-middleware-anthropic-python/blob/main/LICENSE) file for details.

##  Acknowledgments

-  Built by the Revenium team
