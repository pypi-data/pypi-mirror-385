"""Tests for utility functions"""

import os
from unittest.mock import patch

from malti_telemetry import utils
from malti_telemetry.core import get_telemetry_system
from malti_telemetry.utils import extract_ip_from_forwarded_for, is_valid_ip, anonymize_ip


class TestConfiguration:
    """Test configuration utilities"""

    def test_configure_malti(self):
        """Test configuring Malti settings"""
        # Save original environment
        original_env = {}
        env_vars = [
            'MALTI_SERVICE_NAME',
            'MALTI_API_KEY',
            'MALTI_URL',
            'MALTI_NODE',
            'MALTI_BATCH_SIZE',
            'MALTI_BATCH_INTERVAL',
            'MALTI_CLEAN_MODE',
            'MALTI_USE_IP_AS_CONSUMER',
            'MALTI_IP_ANONYMIZE'
        ]

        for var in env_vars:
            if var in os.environ:
                original_env[var] = os.environ[var]

        try:
            # Clear environment
            for var in env_vars:
                os.environ.pop(var, None)

            # Configure Malti
            utils.configure_malti(
                service_name="test-service",
                api_key="test-key",
                malti_url="https://test.example.com",
                node="test-node",
                batch_size=100,
                batch_interval=30.0,
                clean_mode=False,
                use_ip_as_consumer=True,
                ip_anonymize=True
            )

            # Check environment variables were set
            assert os.environ['MALTI_SERVICE_NAME'] == "test-service"
            assert os.environ['MALTI_API_KEY'] == "test-key"
            assert os.environ['MALTI_URL'] == "https://test.example.com"
            assert os.environ['MALTI_NODE'] == "test-node"
            assert os.environ['MALTI_BATCH_SIZE'] == "100"
            assert os.environ['MALTI_BATCH_INTERVAL'] == "30.0"
            assert os.environ['MALTI_CLEAN_MODE'] == "False"
            assert os.environ['MALTI_USE_IP_AS_CONSUMER'] == "True"
            assert os.environ['MALTI_IP_ANONYMIZE'] == "True"

        finally:
            # Restore original environment
            for var in env_vars:
                if var in original_env:
                    os.environ[var] = original_env[var]
                elif var in os.environ:
                    del os.environ[var]

    def test_get_malti_stats(self):
        """Test getting Malti statistics"""
        stats = utils.get_malti_stats()

        # Should return a dictionary
        assert isinstance(stats, dict)
        # Should contain expected keys
        expected_keys = [
            'total_added', 'total_sent', 'total_failed',
            'current_size', 'max_size', 'service_name',
            'node', 'running', 'malti_url', 'clean_mode'
        ]

        for key in expected_keys:
            assert key in stats

    def test_get_telemetry_system_compatibility(self):
        """Test that get_telemetry_system returns a valid system"""
        # Should return a telemetry system instance
        telemetry_system = get_telemetry_system()

        # Should have expected attributes
        assert hasattr(telemetry_system, 'batch_sender')
        assert hasattr(telemetry_system, 'collector')
        assert hasattr(telemetry_system, 'start')
        assert hasattr(telemetry_system, 'stop')
        assert hasattr(telemetry_system, 'record_request')
        assert hasattr(telemetry_system, 'get_stats')


class TestIPUtilities:
    """Test IP address utility functions"""

    def test_extract_ip_from_forwarded_for_single_ip(self):
        """Test extracting single IP from X-Forwarded-For header"""
        result = extract_ip_from_forwarded_for("192.168.1.100")
        assert result == "192.168.1.100"

    def test_extract_ip_from_forwarded_for_multiple_ips(self):
        """Test extracting first IP from multiple IPs in X-Forwarded-For header"""
        result = extract_ip_from_forwarded_for("192.168.1.100, 10.0.0.1, 203.0.113.42")
        assert result == "192.168.1.100"

    def test_extract_ip_from_forwarded_for_ipv6(self):
        """Test extracting IPv6 address from X-Forwarded-For header"""
        result = extract_ip_from_forwarded_for("2001:db8::1, 192.168.1.100")
        assert result == "2001:db8::1"

    def test_extract_ip_from_forwarded_for_with_spaces(self):
        """Test extracting IP with extra spaces"""
        result = extract_ip_from_forwarded_for("  192.168.1.100  ,  10.0.0.1  ")
        assert result == "192.168.1.100"

    def test_extract_ip_from_forwarded_for_invalid_first_ip(self):
        """Test handling invalid first IP in X-Forwarded-For header"""
        result = extract_ip_from_forwarded_for("invalid-ip, 192.168.1.100")
        assert result is None  # Should return None because first IP is invalid

    def test_extract_ip_from_forwarded_for_empty_header(self):
        """Test handling empty X-Forwarded-For header"""
        result = extract_ip_from_forwarded_for("")
        assert result is None

    def test_extract_ip_from_forwarded_for_none_header(self):
        """Test handling None X-Forwarded-For header"""
        result = extract_ip_from_forwarded_for(None)
        assert result is None

    def test_is_valid_ip_ipv4(self):
        """Test IPv4 address validation"""
        assert is_valid_ip("192.168.1.100") is True
        assert is_valid_ip("10.0.0.1") is True
        assert is_valid_ip("203.0.113.42") is True

    def test_is_valid_ip_ipv6(self):
        """Test IPv6 address validation"""
        assert is_valid_ip("2001:db8::1") is True
        assert is_valid_ip("2001:db8:85a3:8d3:1319:8a2e:370:7348") is True
        assert is_valid_ip("::1") is True

    def test_is_valid_ip_invalid(self):
        """Test invalid IP address validation"""
        assert is_valid_ip("invalid-ip") is False
        assert is_valid_ip("999.999.999.999") is False
        assert is_valid_ip("192.168.1") is False
        assert is_valid_ip("") is False

    def test_anonymize_ip_ipv4(self):
        """Test IPv4 address anonymization"""
        result = anonymize_ip("192.168.1.100")
        assert result == "192.168.1.xxx"

    def test_anonymize_ip_ipv6(self):
        """Test IPv6 address anonymization"""
        result = anonymize_ip("2001:db8:85a3:8d3:1319:8a2e:370:7348")
        assert result == "2001:0db8:85a3:08d3:xxxx:xxxx:xxxx:xxxx"

    def test_anonymize_ip_ipv6_short(self):
        """Test IPv6 short address anonymization"""
        result = anonymize_ip("2001:db8::1")
        assert result == "2001:0db8:0000:0000:xxxx:xxxx:xxxx:xxxx"  # Expanded and anonymized

    def test_anonymize_ip_invalid(self):
        """Test anonymizing invalid IP address"""
        result = anonymize_ip("invalid-ip")
        assert result == "invalid-ip"  # Should return original string

    def test_anonymize_ip_empty(self):
        """Test anonymizing empty string"""
        result = anonymize_ip("")
        assert result == ""
