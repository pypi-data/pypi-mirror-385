# Comradecircle Sdk-python

A Python SDK for ComradeCircle's comprehensive social communication and creator economy platform. This SDK provides developers with easy access to ComradeCircle's GraphQL APIs for building communities, managing creators, processing payments, and implementing real-time communication features.

## Features

- 🚀 **Async/await support** - Built with modern Python async patterns
- 🏘️ **Community Management** - Create and manage communities, channels, and members
- 🎨 **Creator Economy** - Handle subscriptions, payments, and revenue analytics
- 💬 **Real-time Communication** - WebSocket support for chat and voice
- 🔐 **Authentication handling** - JWT token management and OAuth integration
- 📦 **Modular architecture** - Organized by ComradeCircle feature modules
- 🔧 **Type hints** - Full typing support with mypy
- 🧪 **Testing ready** - Pytest configuration included
- 📚 **Documentation** - Comprehensive API documentation
- 🛠️ **Development tools** - Code formatting, linting, and pre-commit hooks

## Installation

```bash
# Install from PyPI (when published)
pip install comradecircle-sdk

# Or install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
from comradecircle_sdk import ComradeCircleSDK, ComradeCircleConfig
from comradecircle_sdk.types.community import CommunityCreateInput
from comradecircle_sdk.types.creator import CreatorProfileInput

async def main():
    # Initialize the ComradeCircle SDK
    config = ComradeCircleConfig(
        endpoint="https://api.comradecircle.com/graphql",
        api_key="your-comradecircle-api-key"
    )

    sdk = ComradeCircleSDK(config)

    try:
        # Create a new community
        community_input = CommunityCreateInput(
            name="Tech Creators Hub",
            description="A community for technology creators and developers",
            category="technology",
            is_public=True
        )
        
        community = await sdk.community.create(community_input)
        print(f"Community created: {community.name}")

        # Setup creator profile
        creator_input = CreatorProfileInput(
            display_name="TechGuru",
            bio="Technology content creator and educator",
            subscription_tiers=[
                {"name": "Basic", "price": 5.00, "description": "Access to community chat"},
                {"name": "Premium", "price": 15.00, "description": "All content + monthly Q&A"}
            ]
        )

        creator_profile = await sdk.creator.setup_profile(creator_input)
        print(f"Creator profile setup: {creator_profile.display_name}")
        
        # Set authentication tokens
        sdk.set_tokens(
            access_token="your-access-token",
            refresh_token="your-refresh-token"
        )
        
        # Get current user
        current_user = await sdk.users.get_current_user()
        print(f"Current user: {current_user.name}")
        
    finally:
        await sdk.client.close()

# Run the example
asyncio.run(main())
```

## Configuration

The SDK is configured using the `BoilerSDKConfig` class:

```python
from comradecircle_sdk import BoilerSDKConfig

config = BoilerSDKConfig(
    endpoint="https://api.example.com/graphql",  # Required
    api_key="your-api-key",                      # Optional
    access_token="your-access-token",            # Optional
    refresh_token="your-refresh-token",          # Optional
    timeout=30.0                                 # Optional, default: 30.0
)
```

## Available Modules

The SDK is organized into the following modules:

- **auth** - Authentication operations (register, login, logout, etc.)
- **user** - User management operations
- **workspace** - Workspace operations (TODO)
- **rbac** - Role-based access control (TODO)
- **team** - Team management (TODO)
- **project** - Project operations (TODO)
- **resources** - Resource management (TODO)
- **billing** - Billing operations (TODO)
- **organization** - Organization management (TODO)
- **payment** - Payment processing (TODO)
- **quota** - Quota management (TODO)
- **store** - Store operations (TODO)
- **support** - Support ticket management (TODO)
- **usage** - Usage analytics (TODO)
- **utils** - Utility functions (TODO)
- **addon** - Add-on management (TODO)
- **plan** - Plan management (TODO)
- **product** - Product management (TODO)
- **config** - Configuration management (TODO)

## Examples

See the `examples/` directory for more detailed usage examples:

- `basic_usage.py` - Basic SDK operations
- `advanced_usage.py` - Advanced features and error handling

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd comradecircle-sdk-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black src/ tests/ examples/
isort src/ tests/ examples/

# Lint code
flake8 src/ tests/ examples/
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=comradecircle_sdk --cov-report=html
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=comradecircle_sdk

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

## Project Structure

```
comradecircle-sdk-python/
├── src/
│   └── comradecircle_sdk/
│       ├── __init__.py           # Main SDK class
│       ├── client/               # HTTP/GraphQL client
│       ├── auth/                 # Authentication module
│       ├── user/                 # User management
│       ├── workspace/            # Workspace operations
│       ├── types/                # Type definitions
│       └── ...                   # Other modules
├── tests/                        # Test files
├── examples/                     # Usage examples
├── docs/                         # Documentation
├── pyproject.toml               # Package configuration
├── requirements.txt             # Production dependencies
└── requirements-dev.txt         # Development dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Create a Pull Request

## Type Hints

This SDK is fully typed and supports mypy type checking:

```bash
mypy src/comradecircle_sdk
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Support

- 📖 **Documentation**: [docs.algoshred.com/sdk/python](https://docs.algoshred.com/sdk/python)
- 🐛 **Issues**: [GitHub Issues](https://github.com/algoshred/comradecircle-sdk-python/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/algoshred/comradecircle-sdk-python/discussions)

## Related Projects

- [Workspaces SDK Node.js](../workspaces-sdk-node) - The Node.js version this SDK is based on
- [Boiler Frontend](../comradecircle-frontend) - Frontend comradecircle
- [Boiler Backend](../comradecircle-python-be-graphql) - Python GraphQL backend comradecircle