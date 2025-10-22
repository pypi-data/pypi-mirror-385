"""
Test per config validation enterprise-grade
"""
import pytest
from pydantic import ValidationError

from pyprestascan.core.config_validation import CrawlConfigSchema, validate_crawl_config


class TestCrawlConfigValidation:
    """Test per validazione configurazione"""

    def test_valid_config_minimal(self):
        """Test configurazione minima valida"""
        config = {
            'url': 'https://example.com'
        }
        result = validate_crawl_config(config)
        assert str(result.url) == 'https://example.com/'
        assert result.max_urls == 500  # Default
        assert result.concurrency == 20  # Default

    def test_valid_config_full(self):
        """Test configurazione completa valida"""
        config = {
            'url': 'https://example.com',
            'max_urls': 1000,
            'concurrency': 30,
            'delay': 200,
            'timeout': 20,
            'auth_user': 'user',
            'auth_pass': 'pass',
            'prestashop_mode': True,
            'include_subdomains': False,
            'respect_robots': True
        }
        result = validate_crawl_config(config)
        assert str(result.url) == 'https://example.com/'
        assert result.max_urls == 1000
        assert result.concurrency == 30
        assert result.delay == 200
        assert result.auth_user == 'user'

    def test_invalid_url(self):
        """Test URL non valido"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({'url': 'not-a-url'})
        assert 'url' in str(exc.value)

    def test_invalid_max_urls_negative(self):
        """Test max_urls negativo"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'max_urls': -100
            })
        assert 'max_urls' in str(exc.value)

    def test_invalid_max_urls_too_high(self):
        """Test max_urls troppo alto"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'max_urls': 2000000  # > 1M
            })
        assert 'max_urls' in str(exc.value)

    def test_invalid_concurrency_zero(self):
        """Test concurrency a zero"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'concurrency': 0
            })
        assert 'concurrency' in str(exc.value)

    def test_invalid_concurrency_too_high(self):
        """Test concurrency troppo alta"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'concurrency': 200
            })
        assert 'concurrency' in str(exc.value)

    def test_invalid_delay_negative(self):
        """Test delay negativo"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'delay': -10
            })
        assert 'delay' in str(exc.value)

    def test_high_concurrency_requires_delay(self):
        """Test alta concorrenza richiede delay"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'concurrency': 60,
                'delay': 50  # < 100ms
            })
        assert 'delay' in str(exc.value).lower()
        assert '100ms' in str(exc.value)

    def test_high_concurrency_with_sufficient_delay(self):
        """Test alta concorrenza con delay sufficiente"""
        result = validate_crawl_config({
            'url': 'https://example.com',
            'concurrency': 60,
            'delay': 150
        })
        assert result.concurrency == 60
        assert result.delay == 150

    def test_invalid_timeout_too_low(self):
        """Test timeout troppo basso"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'timeout': 2
            })
        assert 'timeout' in str(exc.value).lower()

    def test_invalid_timeout_too_high(self):
        """Test timeout troppo alto"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'timeout': 120
            })
        assert 'timeout' in str(exc.value).lower()

    def test_auth_password_requires_username(self):
        """Test password senza username fallisce"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'auth_pass': 'password'
            })
        assert 'auth' in str(exc.value).lower()

    def test_auth_username_without_password_ok(self):
        """Test username senza password è valido"""
        result = validate_crawl_config({
            'url': 'https://example.com',
            'auth_user': 'user'
        })
        assert result.auth_user == 'user'
        assert result.auth_pass is None

    def test_memory_requirements_validation(self):
        """Test validazione requisiti memoria"""
        # Configurazione che richiede troppa memoria
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'max_urls': 500000,  # 500K URLs
                'concurrency': 100
            })
        assert 'memoria' in str(exc.value).lower() or 'memory' in str(exc.value).lower()

    def test_large_site_low_concurrency_warning(self):
        """Test sito grande con bassa concorrenza"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'max_urls': 150000,
                'concurrency': 5
            })
        assert 'concurrency' in str(exc.value).lower() or 'ore' in str(exc.value).lower()

    def test_user_agent_too_long(self):
        """Test user agent troppo lungo"""
        with pytest.raises(ValidationError) as exc:
            validate_crawl_config({
                'url': 'https://example.com',
                'user_agent': 'A' * 600  # > 500 chars
            })
        assert 'user' in str(exc.value).lower() and 'agent' in str(exc.value).lower()

    def test_user_agent_reasonable_length(self):
        """Test user agent lunghezza ragionevole"""
        result = validate_crawl_config({
            'url': 'https://example.com',
            'user_agent': 'MyBot/1.0 (custom scanner)'
        })
        assert result.user_agent == 'MyBot/1.0 (custom scanner)'

    def test_config_validation_assigns_defaults(self):
        """Test che la validazione assegna default corretti"""
        result = validate_crawl_config({
            'url': 'https://example.com'
        })
        assert result.prestashop_mode is True
        assert result.respect_robots is True
        assert result.include_subdomains is False
        assert result.resume is False
        assert result.delay == 0

    def test_schema_url_normalization(self):
        """Test che URL vengono normalizzati"""
        result = validate_crawl_config({
            'url': 'https://example.com'
        })
        # Pydantic aggiunge trailing slash
        assert str(result.url).endswith('/')

    def test_realistic_ecommerce_config(self):
        """Test configurazione realistica per e-commerce"""
        config = {
            'url': 'https://myshop.com',
            'max_urls': 5000,
            'concurrency': 25,
            'delay': 100,
            'timeout': 20,
            'prestashop_mode': True,
            'respect_robots': True
        }
        result = validate_crawl_config(config)
        assert result.max_urls == 5000
        assert result.concurrency == 25
        assert result.prestashop_mode is True

    def test_realistic_large_site_config(self):
        """Test configurazione per sito grande"""
        config = {
            'url': 'https://largeshop.com',
            'max_urls': 15000,  # Entro limite memoria (15000 * 0.05 + 40 * 0.1 = 754MB)
            'concurrency': 40,
            'delay': 150,
            'timeout': 25
        }
        result = validate_crawl_config(config)
        assert result.max_urls == 15000
        assert result.concurrency == 40

    def test_config_immutability_after_validation(self):
        """Test che config validato può essere rivalidato"""
        config = {'url': 'https://example.com', 'max_urls': 100}
        result1 = validate_crawl_config(config)
        # Modifica config originale
        config['max_urls'] = 200
        # Rivalidazione dovrebbe usare nuovo valore
        result2 = validate_crawl_config(config)
        assert result1.max_urls == 100
        assert result2.max_urls == 200
