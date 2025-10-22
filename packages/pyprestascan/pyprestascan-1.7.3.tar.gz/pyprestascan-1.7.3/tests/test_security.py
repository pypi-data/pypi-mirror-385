"""
Test per security validation
"""
import pytest

from pyprestascan.core.security import SecurityValidator, SecurityError, validate_url_safe


class TestSecurityValidator:
    """Test per SecurityValidator"""

    def test_valid_http_url(self):
        """Test URL HTTP valido"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://example.com")
        assert is_valid is True
        assert error is None

    def test_valid_https_url(self):
        """Test URL HTTPS valido"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("https://example.com")
        assert is_valid is True
        assert error is None

    def test_invalid_schema_ftp(self):
        """Test schema non permesso (FTP)"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("ftp://example.com")
        assert is_valid is False
        assert "Schema non permesso" in error

    def test_invalid_schema_file(self):
        """Test schema non permesso (file://)"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("file:///etc/passwd")
        assert is_valid is False
        assert "Schema non permesso" in error

    def test_localhost_blocked_by_default(self):
        """Test che localhost è bloccato di default"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://localhost")
        assert is_valid is False
        assert "Localhost" in error

    def test_localhost_allowed_when_enabled(self):
        """Test che localhost funziona se abilitato"""
        validator = SecurityValidator(allow_localhost=True)
        is_valid, error = validator.validate_url("http://localhost")
        assert is_valid is True
        assert error is None

    def test_127_0_0_1_blocked(self):
        """Test che 127.0.0.1 è bloccato"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://127.0.0.1")
        assert is_valid is False
        assert "loopback" in error.lower() or "localhost" in error.lower()

    def test_private_ip_10_blocked(self):
        """Test che IP privato 10.x è bloccato"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://10.0.0.1")
        assert is_valid is False
        assert "privato" in error.lower() or "private" in error.lower()

    def test_private_ip_192_168_blocked(self):
        """Test che IP privato 192.168.x è bloccato"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://192.168.1.1")
        assert is_valid is False
        assert "privato" in error.lower() or "private" in error.lower()

    def test_private_ip_172_16_blocked(self):
        """Test che IP privato 172.16.x è bloccato"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://172.16.0.1")
        assert is_valid is False
        assert "privato" in error.lower() or "private" in error.lower()

    def test_private_ips_allowed_when_enabled(self):
        """Test che IP privati funzionano se abilitati"""
        validator = SecurityValidator(allow_private_ips=True)
        is_valid, error = validator.validate_url("http://192.168.1.1")
        assert is_valid is True
        assert error is None

    def test_link_local_blocked(self):
        """Test che link-local (169.254.x.x) è bloccato"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://169.254.0.1")
        assert is_valid is False

    def test_ipv6_loopback_blocked(self):
        """Test che IPv6 loopback è bloccato"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://[::1]")
        assert is_valid is False
        assert "loopback" in error.lower() or "localhost" in error.lower()

    def test_restricted_port_3306_blocked(self):
        """Test che porta MySQL (3306) è bloccata"""
        validator = SecurityValidator(allow_localhost=True)
        is_valid, error = validator.validate_url("http://localhost:3306")
        assert is_valid is False
        assert "porta" in error.lower() or "port" in error.lower()
        assert "3306" in error

    def test_restricted_port_6379_blocked(self):
        """Test che porta Redis (6379) è bloccata"""
        validator = SecurityValidator(allow_localhost=True)
        is_valid, error = validator.validate_url("http://localhost:6379")
        assert is_valid is False
        assert "6379" in error

    def test_standard_port_80_allowed(self):
        """Test che porta 80 è permessa"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://example.com:80")
        assert is_valid is True
        assert error is None

    def test_standard_port_443_allowed(self):
        """Test che porta 443 è permessa"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("https://example.com:443")
        assert is_valid is True
        assert error is None

    def test_url_encoding_bypass_blocked(self):
        """Test che URL encoding bypass è bloccato"""
        validator = SecurityValidator()
        # %6c%6f%63%61%6c%68%6f%73%74 = localhost
        is_valid, error = validator.validate_url("http://%6c%6f%63%61%6c%68%6f%73%74")
        assert is_valid is False
        assert "sospetti" in error.lower() or "bypass" in error.lower()

    def test_hex_ip_bypass_blocked(self):
        """Test che hex IP representation è bloccata"""
        validator = SecurityValidator()
        # 0x7f.0x0.0x0.0x1 = 127.0.0.1
        is_valid, error = validator.validate_url("http://0x7f.0x0.0x0.0x1")
        assert is_valid is False
        assert "sospetti" in error.lower() or "bypass" in error.lower()

    def test_decimal_ip_bypass_blocked(self):
        """Test che decimal IP representation è bloccata"""
        validator = SecurityValidator()
        # 2130706433 = 127.0.0.1 in decimal
        is_valid, error = validator.validate_url("http://2130706433")
        assert is_valid is False
        assert "sospetti" in error.lower() or "bypass" in error.lower()

    def test_at_sign_trick_blocked(self):
        """Test che @ trick con localhost è bloccato"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://user:pass@localhost")
        assert is_valid is False

    def test_lvh_me_blocked(self):
        """Test che lvh.me (localhost alias) è bloccato"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://lvh.me")
        assert is_valid is False
        assert "localhost" in error.lower()

    def test_url_with_path_valid(self):
        """Test URL con path valido"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("https://example.com/path/to/resource")
        assert is_valid is True
        assert error is None

    def test_url_with_query_valid(self):
        """Test URL con query string valido"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("https://example.com/search?q=test")
        assert is_valid is True
        assert error is None

    def test_validate_url_strict_raises(self):
        """Test che validate_url_strict raise exception"""
        validator = SecurityValidator()
        with pytest.raises(SecurityError, match="Localhost"):
            validator.validate_url_strict("http://localhost")

    def test_validate_url_strict_passes(self):
        """Test che validate_url_strict non raise se valido"""
        validator = SecurityValidator()
        # Non dovrebbe raise
        validator.validate_url_strict("https://example.com")

    def test_validate_url_safe_helper(self):
        """Test funzione helper validate_url_safe"""
        assert validate_url_safe("https://example.com") is True
        assert validate_url_safe("http://localhost") is False
        assert validate_url_safe("http://localhost", allow_localhost=True) is True

    def test_no_hostname_invalid(self):
        """Test URL senza hostname"""
        validator = SecurityValidator()
        is_valid, error = validator.validate_url("http://")
        assert is_valid is False
        assert "hostname" in error.lower()

    def test_real_world_urls(self):
        """Test URL reali comuni"""
        validator = SecurityValidator()

        # Validi
        valid_urls = [
            "https://google.com",
            "https://github.com/user/repo",
            "http://example.com:8000",
            "https://subdomain.example.com",
            "https://example.com/path?param=value#anchor"
        ]

        for url in valid_urls:
            is_valid, error = validator.validate_url(url)
            assert is_valid is True, f"URL dovrebbe essere valido: {url}, error: {error}"

        # Invalidi (security risks)
        invalid_urls = [
            "http://localhost",
            "http://127.0.0.1",
            "http://192.168.1.1",
            "http://10.0.0.1",
            "http://[::1]",
            "ftp://example.com",
            "file:///etc/passwd",
            "http://example.com:3306"
        ]

        for url in invalid_urls:
            is_valid, error = validator.validate_url(url)
            assert is_valid is False, f"URL dovrebbe essere invalido: {url}"

    def test_cloud_metadata_endpoints_blocked(self):
        """Test che cloud metadata endpoints sono bloccati"""
        validator = SecurityValidator()

        # AWS metadata
        is_valid, error = validator.validate_url("http://169.254.169.254/latest/meta-data")
        assert is_valid is False

        # GCP metadata (link-local)
        is_valid, error = validator.validate_url("http://169.254.169.254/computeMetadata/v1")
        assert is_valid is False
