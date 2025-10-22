"""
Security validation per enterprise-grade protection
"""
import ipaddress
from urllib.parse import urlparse
from typing import Optional, Set
import re


class SecurityValidator:
    """
    Validatore security per prevenzione attacchi comuni

    Features:
    - SSRF (Server-Side Request Forgery) protection
    - Private IP blocking
    - Localhost blocking
    - Schema whitelisting
    - Port restriction
    """

    # Private IP ranges (RFC 1918, RFC 4193, RFC 6598)
    PRIVATE_IP_RANGES = [
        ipaddress.ip_network('10.0.0.0/8'),          # Class A private
        ipaddress.ip_network('172.16.0.0/12'),       # Class B private
        ipaddress.ip_network('192.168.0.0/16'),      # Class C private
        ipaddress.ip_network('127.0.0.0/8'),         # Loopback
        ipaddress.ip_network('169.254.0.0/16'),      # Link-local
        ipaddress.ip_network('::1/128'),             # IPv6 loopback
        ipaddress.ip_network('fe80::/10'),           # IPv6 link-local
        ipaddress.ip_network('fc00::/7'),            # IPv6 unique local
        ipaddress.ip_network('100.64.0.0/10'),       # Shared address space (CGN)
    ]

    # Hostname blacklist (localhost aliases)
    LOCALHOST_HOSTNAMES = {
        'localhost',
        'localhost.localdomain',
        'lvh.me',  # DNS wildcard che punta a 127.0.0.1
        '127.0.0.1',
        '0.0.0.0',
        '::1',
        '0:0:0:0:0:0:0:1',
    }

    # Schema whitelist
    ALLOWED_SCHEMAS = {'http', 'https'}

    # Restricted ports (common internal services)
    RESTRICTED_PORTS = {
        22,    # SSH
        23,    # Telnet
        25,    # SMTP
        3306,  # MySQL
        5432,  # PostgreSQL
        6379,  # Redis
        9200,  # Elasticsearch
        27017, # MongoDB
        5000,  # Dev servers
        8080,  # Proxy/Dev
    }

    def __init__(self, allow_localhost: bool = False, allow_private_ips: bool = False):
        """
        Inizializza validator

        Args:
            allow_localhost: Se True, permette localhost (default: False)
            allow_private_ips: Se True, permette IP privati (default: False)
        """
        self.allow_localhost = allow_localhost
        self.allow_private_ips = allow_private_ips

    def validate_url(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Valida URL per security issues

        Args:
            url: URL da validare

        Returns:
            (is_valid, error_message)
            - is_valid: True se URL è sicuro
            - error_message: Messaggio errore se non valido, None altrimenti

        Examples:
            >>> validator = SecurityValidator()
            >>> validator.validate_url("http://example.com")
            (True, None)
            >>> validator.validate_url("http://localhost")
            (False, "Localhost URLs not allowed...")
        """
        try:
            parsed = urlparse(url)

            # Validazione schema
            if parsed.scheme not in self.ALLOWED_SCHEMAS:
                return False, f"Schema non permesso: {parsed.scheme}. Usare solo: {', '.join(self.ALLOWED_SCHEMAS)}"

            # Validazione hostname
            if not parsed.hostname:
                return False, "URL non contiene hostname valido"

            hostname = parsed.hostname.lower()

            # Check localhost
            if not self.allow_localhost and hostname in self.LOCALHOST_HOSTNAMES:
                return False, (
                    f"Localhost URLs non permessi per sicurezza (hostname: {hostname}). "
                    f"Usa allow_localhost=True per abilitare."
                )

            # Check IP address vs hostname
            try:
                ip_addr = ipaddress.ip_address(hostname)

                # Check if IP is private
                if not self.allow_private_ips:
                    if self._is_private_ip(ip_addr):
                        return False, (
                            f"IP privato/interno non permesso: {ip_addr}. "
                            f"Usa allow_private_ips=True per abilitare."
                        )

                # Check loopback
                if not self.allow_localhost and ip_addr.is_loopback:
                    return False, (
                        f"IP loopback non permesso: {ip_addr}. "
                        f"Usa allow_localhost=True per abilitare."
                    )

            except ValueError:
                # Non è un IP, è un hostname - OK
                pass

            # Check porta riservata
            port = parsed.port
            if port and port in self.RESTRICTED_PORTS:
                return False, (
                    f"Porta riservata non permessa: {port}. "
                    f"Porte bloccate: {sorted(self.RESTRICTED_PORTS)}"
                )

            # Check per bypass tricks comuni (URL encoding, unicode, etc.)
            if self._contains_bypass_tricks(url):
                return False, (
                    "URL contiene caratteri sospetti (possibile bypass tentativo). "
                    "Usare solo URL standard."
                )

            return True, None

        except Exception as e:
            return False, f"Errore validazione URL: {e}"

    def _is_private_ip(self, ip_addr: ipaddress._BaseAddress) -> bool:
        """Check se IP è privato/interno"""
        for private_range in self.PRIVATE_IP_RANGES:
            if ip_addr in private_range:
                return True
        return False

    def _contains_bypass_tricks(self, url: str) -> bool:
        """
        Rileva common bypass tricks:
        - URL encoding (% characters in hostname)
        - Unicode tricks
        - @ tricks (user:pass@internal)
        - Alternative IP representations (hex, octal, decimal)
        """
        # Check URL encoding nel hostname
        if '%' in url.split('/')[2]:  # hostname part
            return True

        # Check @ trick (username:password@internal-host)
        if '@' in url.split('/')[2]:  # hostname part
            parsed = urlparse(url)
            # @ è ok solo se c'è auth, ma hostname non deve essere localhost
            if parsed.hostname and parsed.hostname.lower() in self.LOCALHOST_HOSTNAMES:
                return True

        # Check hex/octal IP representations
        # Esempio: http://0x7f.0x0.0x0.0x1 = 127.0.0.1
        hostname_part = urlparse(url).hostname or ''
        if re.match(r'.*0x[0-9a-f]+.*', hostname_part, re.IGNORECASE):
            return True

        # Check decimal IP (http://2130706433 = 127.0.0.1)
        if hostname_part.isdigit() and int(hostname_part) > 0xFFFFFF:
            return True

        return False

    def validate_url_strict(self, url: str) -> None:
        """
        Validazione strict che raise exception se non valido

        Args:
            url: URL da validare

        Raises:
            SecurityError: Se URL non passa validazione

        Examples:
            >>> validator = SecurityValidator()
            >>> validator.validate_url_strict("http://example.com")  # OK
            >>> validator.validate_url_strict("http://localhost")  # Raises SecurityError
        """
        is_valid, error_msg = self.validate_url(url)
        if not is_valid:
            raise SecurityError(error_msg)


class SecurityError(Exception):
    """Exception per errori di sicurezza"""
    pass


# Funzioni helper per backward compatibility
def validate_url_safe(url: str, allow_localhost: bool = False) -> bool:
    """
    Valida URL ritornando solo bool

    Args:
        url: URL da validare
        allow_localhost: Permetti localhost

    Returns:
        True se URL è sicuro, False altrimenti
    """
    validator = SecurityValidator(allow_localhost=allow_localhost)
    is_valid, _ = validator.validate_url(url)
    return is_valid


# Export
__all__ = [
    'SecurityValidator',
    'SecurityError',
    'validate_url_safe'
]
