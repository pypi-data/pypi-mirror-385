"""
Unit tests for jinfo CLI module.

Tests cover:
- Successful NETCONF connections and data retrieval
- Various exception scenarios (timeout, auth failure, host unreachable, etc.)
- XML parsing edge cases
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import AuthenticationError, SessionCloseError, SSHError

from jinfo.cli import get_juniper_version, main


class TestGetJuniperVersion:
    """Test cases for get_juniper_version function."""

    @patch("jinfo.cli.manager.connect")
    def test_successful_connection_and_data_retrieval(self, mock_connect):
        """Test successful NETCONF connection and version retrieval."""
        # Mock XML response
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-information>
                <host-name>router1.example.com</host-name>
                <product-model>MX960</product-model>
                <junos-version>20.4R3-S1.1</junos-version>
            </software-information>
        </rpc-reply>"""

        # Setup mock manager and RPC response
        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value=xml_response)
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        # Execute function
        result = get_juniper_version("router1.example.com", "testuser", 830)

        # Verify results
        assert result == {
            "host-name": "router1.example.com",
            "product-model": "MX960",
            "junos-version": "20.4R3-S1.1",
        }

        # Verify manager was called correctly
        mock_connect.assert_called_once_with(
            host="router1.example.com",
            port=830,
            username="testuser",
            device_params={"name": "junos"},
            hostkey_verify=False,
            timeout=30,
        )
        mock_manager.get_software_information.assert_called_once()

    @patch("jinfo.cli.manager.connect")
    def test_successful_connection_with_minimal_data(self, mock_connect):
        """Test successful connection with only required fields."""
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-information>
                <host-name>switch1</host-name>
                <product-model>EX4300</product-model>
                <junos-version>21.1R1</junos-version>
            </software-information>
        </rpc-reply>"""

        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value=xml_response)
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        result = get_juniper_version("192.168.1.1", "admin")

        assert result == {
            "host-name": "switch1",
            "product-model": "EX4300",
            "junos-version": "21.1R1",
        }

    @patch("jinfo.cli.manager.connect")
    def test_successful_connection_with_extra_fields(self, mock_connect):
        """Test that extra fields in response are ignored."""
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-information>
                <host-name>firewall1</host-name>
                <product-model>SRX4600</product-model>
                <junos-version>21.2R3</junos-version>
                <package-information>
                    <name>junos</name>
                    <comment>JUNOS Base OS boot</comment>
                </package-information>
                <cli>
                    <banner>Welcome</banner>
                </cli>
            </software-information>
        </rpc-reply>"""

        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value=xml_response)
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        result = get_juniper_version("10.0.0.1", "user1")

        # Should only contain the three required fields
        assert len(result) == 3
        assert result["host-name"] == "firewall1"
        assert result["product-model"] == "SRX4600"
        assert result["junos-version"] == "21.2R3"

    @patch("jinfo.cli.manager.connect")
    def test_connection_timeout_exception(self, mock_connect):
        """Test handling of connection timeout exception."""
        mock_connect.side_effect = TimeoutExpiredError("Connection timeout after 30 seconds")

        with pytest.raises(ConnectionError) as exc_info:
            get_juniper_version("slow-router", "admin")

        assert "Failed to connect to slow-router" in str(exc_info.value)
        assert "Connection timeout" in str(exc_info.value)

    @patch("jinfo.cli.manager.connect")
    def test_authentication_failure_exception(self, mock_connect):
        """Test handling of authentication failure."""
        mock_connect.side_effect = AuthenticationError("Authentication failed")

        with pytest.raises(ConnectionError) as exc_info:
            get_juniper_version("router1", "wronguser")

        assert "Failed to connect to router1" in str(exc_info.value)
        assert "Authentication failed" in str(exc_info.value)

    @patch("jinfo.cli.manager.connect")
    def test_ssh_error_exception(self, mock_connect):
        """Test handling of SSH connection error."""
        mock_connect.side_effect = SSHError("Unable to establish SSH connection")

        with pytest.raises(ConnectionError) as exc_info:
            get_juniper_version("unreachable-host", "user")

        assert "Failed to connect to unreachable-host" in str(exc_info.value)

    @patch("jinfo.cli.manager.connect")
    def test_session_close_error_exception(self, mock_connect):
        """Test handling of session close error."""
        mock_connect.side_effect = SessionCloseError("Session closed unexpectedly")

        with pytest.raises(ConnectionError) as exc_info:
            get_juniper_version("router1", "user")

        assert "Failed to connect to router1" in str(exc_info.value)

    @patch("jinfo.cli.manager.connect")
    def test_rpc_error_exception(self, mock_connect):
        """Test handling of RPC error during get_software_information."""
        mock_manager = MagicMock()
        # Create a mock RPC error
        mock_rpc_error = MagicMock(spec=RPCError)
        mock_rpc_error.__str__ = Mock(return_value="RPC operation failed")
        mock_manager.get_software_information.side_effect = mock_rpc_error
        mock_connect.return_value.__enter__.return_value = mock_manager

        with pytest.raises(ConnectionError) as exc_info:
            get_juniper_version("router1", "user")

        assert "Failed to connect to router1" in str(exc_info.value)

    @patch("jinfo.cli.manager.connect")
    def test_generic_exception_handling(self, mock_connect):
        """Test handling of unexpected exceptions."""
        mock_connect.side_effect = Exception("Unexpected error occurred")

        with pytest.raises(ConnectionError) as exc_info:
            get_juniper_version("router1", "user")

        assert "Failed to connect to router1" in str(exc_info.value)
        assert "Unexpected error occurred" in str(exc_info.value)

    @patch("jinfo.cli.manager.connect")
    def test_invalid_xml_response(self, mock_connect):
        """Test handling of invalid XML response."""
        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value="<invalid><xml>")
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        with pytest.raises(ConnectionError) as exc_info:
            get_juniper_version("router1", "user")

        assert "Failed to connect to router1" in str(exc_info.value)

    @patch("jinfo.cli.manager.connect")
    def test_empty_xml_response(self, mock_connect):
        """Test handling of empty XML response."""
        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value="")
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        # Empty XML should raise ConnectionError due to XML parsing failure
        with pytest.raises(ConnectionError) as exc_info:
            get_juniper_version("router1", "user")

        assert "Failed to connect to router1" in str(exc_info.value)

    @patch("jinfo.cli.manager.connect")
    def test_missing_version_fields(self, mock_connect):
        """Test handling of missing version fields in response."""
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-information>
                <host-name>router1</host-name>
                <!-- Missing product-model and junos-version -->
            </software-information>
        </rpc-reply>"""

        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value=xml_response)
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        result = get_juniper_version("router1", "user")

        # Should only contain the fields that were present
        assert result == {"host-name": "router1"}

    @patch("jinfo.cli.manager.connect")
    def test_whitespace_in_version_fields(self, mock_connect):
        """Test handling of whitespace in version fields."""
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-information>
                <host-name>  router1  </host-name>
                <product-model>
                    MX960
                </product-model>
                <junos-version>  20.4R3-S1.1  </junos-version>
            </software-information>
        </rpc-reply>"""

        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value=xml_response)
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        result = get_juniper_version("router1", "user")

        # Whitespace should be stripped
        assert result == {
            "host-name": "router1",
            "product-model": "MX960",
            "junos-version": "20.4R3-S1.1",
        }

    @patch("jinfo.cli.manager.connect")
    def test_custom_port_number(self, mock_connect):
        """Test connection with custom port number."""
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-information>
                <host-name>router1</host-name>
                <product-model>MX960</product-model>
                <junos-version>20.4R3</junos-version>
            </software-information>
        </rpc-reply>"""

        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value=xml_response)
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        result = get_juniper_version("router1", "user", port=2222)

        # Verify custom port was used
        mock_connect.assert_called_once_with(
            host="router1",
            port=2222,
            username="user",
            device_params={"name": "junos"},
            hostkey_verify=False,
            timeout=30,
        )

        assert result["host-name"] == "router1"


class TestMain:
    """Test cases for main CLI function."""

    @patch("jinfo.cli.get_juniper_version")
    @patch("jinfo.cli.os.getenv")
    @patch("jinfo.cli.sys.argv", ["jinfo", "testhost"])
    def test_main_success(self, mock_getenv, mock_get_version):
        """Test successful execution of main function."""
        mock_getenv.return_value = "testuser"
        mock_get_version.return_value = {
            "host-name": "router1",
            "product-model": "MX960",
            "junos-version": "20.4R3",
        }

        result = main()

        assert result == 0
        mock_get_version.assert_called_once_with(host="testhost", username="testuser", port=830)

    @patch("jinfo.cli.get_juniper_version")
    @patch("jinfo.cli.os.getenv")
    @patch("jinfo.cli.sys.argv", ["jinfo", "testhost"])
    def test_main_connection_error(self, mock_getenv, mock_get_version):
        """Test main function handling connection error."""
        mock_getenv.return_value = "testuser"
        mock_get_version.side_effect = ConnectionError("Failed to connect")

        result = main()

        assert result == 1

    @patch("jinfo.cli.os.getenv")
    @patch("jinfo.cli.sys.argv", ["jinfo", "testhost"])
    def test_main_no_username(self, mock_getenv):
        """Test main function when username cannot be determined."""
        mock_getenv.return_value = None

        result = main()

        assert result == 1

    @patch("jinfo.cli.get_juniper_version")
    @patch("jinfo.cli.os.getenv")
    @patch("jinfo.cli.sys.argv", ["jinfo", "testhost"])
    def test_main_unexpected_error(self, mock_getenv, mock_get_version):
        """Test main function handling unexpected errors."""
        mock_getenv.return_value = "testuser"
        mock_get_version.side_effect = Exception("Unexpected error")

        result = main()

        assert result == 1


class TestIntegrationScenarios:
    """Integration-style tests for common real-world scenarios."""

    @patch("jinfo.cli.manager.connect")
    def test_firewall_device_connection(self, mock_connect):
        """Test connection to SRX firewall device."""
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-information>
                <host-name>srx1.company.com</host-name>
                <product-model>SRX4600</product-model>
                <junos-version>21.4R3-S2.1</junos-version>
            </software-information>
        </rpc-reply>"""

        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value=xml_response)
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        result = get_juniper_version("srx1.company.com", "network-admin")

        assert result["product-model"] == "SRX4600"
        assert "21.4R3" in result["junos-version"]

    @patch("jinfo.cli.manager.connect")
    def test_switch_device_connection(self, mock_connect):
        """Test connection to EX switch device."""
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-information>
                <host-name>ex-switch-01</host-name>
                <product-model>EX4300-48MP</product-model>
                <junos-version>21.1R3-S5.3</junos-version>
            </software-information>
        </rpc-reply>"""

        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value=xml_response)
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        result = get_juniper_version("192.168.10.50", "admin")

        assert "EX4300" in result["product-model"]
        assert result["host-name"] == "ex-switch-01"

    @patch("jinfo.cli.manager.connect")
    def test_router_device_connection(self, mock_connect):
        """Test connection to MX router device."""
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-information>
                <host-name>mx-core-01</host-name>
                <product-model>MX960</product-model>
                <junos-version>20.4R3-S4.2</junos-version>
            </software-information>
        </rpc-reply>"""

        mock_manager = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.__str__ = Mock(return_value=xml_response)
        mock_manager.get_software_information.return_value = mock_rpc
        mock_connect.return_value.__enter__.return_value = mock_manager

        result = get_juniper_version("10.0.0.1", "operator")

        assert result["product-model"] == "MX960"
        assert "20.4R3" in result["junos-version"]

    @patch("jinfo.cli.manager.connect")
    def test_hostname_resolution_failure(self, mock_connect):
        """Test handling of hostname resolution failure."""
        mock_connect.side_effect = Exception("Name or service not known")

        with pytest.raises(ConnectionError) as exc_info:
            get_juniper_version("nonexistent-host.example.com", "user")

        assert "Failed to connect to nonexistent-host.example.com" in str(exc_info.value)

    @patch("jinfo.cli.manager.connect")
    def test_port_unreachable(self, mock_connect):
        """Test handling of unreachable port."""
        mock_connect.side_effect = Exception("Connection refused")

        with pytest.raises(ConnectionError) as exc_info:
            get_juniper_version("192.168.1.100", "user", port=830)

        assert "Failed to connect to 192.168.1.100" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
