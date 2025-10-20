# Jinfo - Juniper Device Information Tool

A Python CLI tool that connects to Juniper devices via NETCONF and retrieves software version information.

## Features

- Connect to Juniper devices via NETCONF
- Retrieve software version information
- Output results in JSON format
- SSH key-based authentication (no password required)

## Requirements

- Python 3.10 or higher
- SSH key configured on the Juniper device for the user running the script
- NETCONF enabled on the target Juniper device

## Installation

Install the required dependencies:

```bash
pip install -e .
```

## Usage

After installation, use the `jinfo` command:

```bash
jinfo <device-hostname>
```

### Arguments

- `hostname`: Juniper device hostname or IP address (required)

### Examples

```bash
# Connect to a device
jinfo router1.example.com

# Connect using IP address
jinfo 192.168.1.1

# Connect to any Juniper device
jinfo juniper-device
```

### Output

The tool outputs software version information in JSON format:

```json
{
  "host-name": "router1",
  "product-model": "MX480",
  "junos-version": "21.2R3-S1.7"
}
```

## Configuration

Before running the tool, ensure:

1. Your SSH public key is added to the Juniper device
2. NETCONF is enabled on the device:
   ```
   set system services netconf ssh
   commit
   ```
3. The device is reachable on the specified port (default: 830)

## Versioning

This project uses [Semantic Versioning](https://semver.org/) based on [Conventional Commits](https://www.conventionalcommits.org/). 

Versions are automatically determined from commit messages:
- `feat:` → Minor version bump (0.1.0 → 0.2.0)
- `fix:` → Patch version bump (0.1.0 → 0.1.1)
- `feat!:` or `BREAKING CHANGE:` → Major version bump (0.1.0 → 1.0.0)

See [SEMANTIC_VERSIONING.md](SEMANTIC_VERSIONING.md) for detailed information.

## License

MIT
# Test
# Test feature
# Trigger release
# Test
