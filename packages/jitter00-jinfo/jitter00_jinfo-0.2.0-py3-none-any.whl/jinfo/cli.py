#!/usr/bin/env python3
"""
Jinfo - Juniper device information retrieval tool via NETCONF

This tool connects to a Juniper device via NETCONF and retrieves
software version information (equivalent to "show version").
"""

import argparse
import json
import os
import sys
from xml.etree import ElementTree as ET

from ncclient import manager


def get_juniper_version(host, username, port=830):
    """
    Connect to Juniper device via NETCONF and retrieve software version.

    Args:
        host: Device hostname or IP address
        username: Username for authentication
        port: NETCONF port (default: 830)

    Returns:
        dict: Software version information
    """
    try:
        # Connect to device using SSH key authentication
        with manager.connect(
            host=host,
            port=port,
            username=username,
            device_params={"name": "junos"},
            hostkey_verify=False,
            timeout=30,
        ) as m:
            # Execute the get-software-information RPC (equivalent to "show version")
            rpc = m.get_software_information()

            # Parse the XML response
            root = ET.fromstring(str(rpc))

            # Extract only the required version information
            version_info = {}

            # Find specific elements
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    tag_name = elem.tag.split("}")[-1]  # Remove namespace

                    # Only include the three required keys
                    if tag_name in ["host-name", "product-model", "junos-version"]:
                        version_info[tag_name] = elem.text.strip()

            return version_info

    except Exception as e:
        raise ConnectionError(f"Failed to connect to {host}: {str(e)}") from e


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Retrieve Juniper device software version via NETCONF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s router1.example.com
  %(prog)s 192.168.1.1
  %(prog)s juniper-device
        """,
    )

    parser.add_argument("host", help="Juniper device hostname or IP address")

    args = parser.parse_args()

    # Get username from environment
    username = os.getenv("USER") or os.getenv("USERNAME")
    if not username:
        print("Error: Could not determine username from environment", file=sys.stderr)
        return 1

    try:
        # Retrieve version information
        version_info = get_juniper_version(host=args.host, username=username, port=830)

        # Output as JSON
        print(json.dumps(version_info, indent=2))

        return 0

    except ConnectionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
