# Vigil Science

**Complete reproducible science platform**

Vigil Science provides a unified CLI for reproducible science workflows, combining cryptographic provenance with platform integration.

## Installation

```bash
pip install vigil-science
```

## Quick Start

```bash
# Initialize a new project
vigil init my-project
cd my-project

# Generate signing keys
vigil signing generate-keypair

# Run experiments
vigil run python experiment.py

# Generate receipt
vigil promote

# Verify reproducibility
vigil verify

# Upload to platform (optional)
vigil login
vigil push
```

## What's Included

This package provides the complete Vigil platform:

- **vigil-core**: Cryptographic operations, local reproducibility, CLI tools
- **vigil-client**: Platform integration, authentication, artifact management

## Commands

### Core Commands
- `vigil init` - Initialize new project
- `vigil run` - Execute reproducible workflows
- `vigil promote` - Generate cryptographic receipts
- `vigil verify` - Verify reproducibility
- `vigil doctor` - Health check and diagnostics

### Platform Commands
- `vigil login` - Authenticate with platform
- `vigil push` - Upload verified artifacts
- `vigil pull` - Download artifacts
- `vigil search` - Search platform artifacts

### Utility Commands
- `vigil signing generate-keypair` - Generate Ed25519 keys
- `vigil signing sign` - Sign receipts
- `vigil signing verify` - Verify signatures
- `vigil completion` - Generate shell completions

## Documentation

- [Getting Started](https://docs.vigil.cofactor.app/getting-started)
- [CLI Reference](https://docs.vigil.cofactor.app/cli-reference)
- [Architecture](https://docs.vigil.cofactor.app/architecture)

## Support

- [GitHub Issues](https://github.com/cofactor/vigil/issues)
- [Documentation](https://docs.vigil.cofactor.app)
- [Community](https://discord.gg/vigil)

## License

Apache 2.0 - see [LICENSE](LICENSE) for details.
