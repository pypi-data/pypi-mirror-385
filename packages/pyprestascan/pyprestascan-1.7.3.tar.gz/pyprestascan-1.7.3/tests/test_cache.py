"""
Test per modulo cache
"""
import pytest
import time
import threading
from pyprestascan.core.cache import (
    LRUCache,
    CacheEntry,
    CacheStats,
    cached
)


class TestCacheEntry:
    """Test per CacheEntry"""

    def test_entry_creation(self):
        """Test creazione entry base"""
        entry = CacheEntry(value="test_value")
        assert entry.value == "test_value"
        assert entry.ttl_seconds is None
        assert not entry.is_expired()

    def test_entry_with_ttl_not_expired(self):
        """Test entry con TTL non scaduta"""
        entry = CacheEntry(value="test", ttl_seconds=10.0)
        assert not entry.is_expired()

    def test_entry_with_ttl_expired(self):
        """Test entry con TTL scaduta"""
        entry = CacheEntry(value="test", ttl_seconds=0.1)
        time.sleep(0.15)  # Attendi scadenza
        assert entry.is_expired()

    def test_entry_no_ttl_never_expires(self):
        """Test entry senza TTL non scade mai"""
        entry = CacheEntry(value="test", ttl_seconds=None)
        time.sleep(0.1)
        assert not entry.is_expired()


class TestCacheStats:
    """Test per CacheStats"""

    def test_stats_initialization(self):
        """Test inizializzazione statistiche"""
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0
        assert stats.expirations == 0

    def test_hit_rate_empty(self):
        """Test hit rate con cache vuota"""
        stats = CacheStats()
        assert stats.hit_rate == 0.0

    def test_hit_rate_calculation(self):
        """Test calcolo hit rate"""
        stats = CacheStats(hits=80, misses=20)
        assert stats.hit_rate == 80.0

    def test_total_requests(self):
        """Test conteggio totale richieste"""
        stats = CacheStats(hits=75, misses=25)
        assert stats.total_requests == 100

    def test_to_dict(self):
        """Test export come dizionario"""
        stats = CacheStats(hits=60, misses=40, evictions=5, expirations=3)
        result = stats.to_dict()

        assert result['hits'] == 60
        assert result['misses'] == 40
        assert result['evictions'] == 5
        assert result['expirations'] == 3
        assert result['hit_rate_pct'] == 60.0
        assert result['total_requests'] == 100


class TestLRUCache:
    """Test per LRUCache"""

    def test_cache_initialization(self):
        """Test inizializzazione cache"""
        cache = LRUCache[str](max_size=100)
        assert cache.max_size == 100
        assert cache.size() == 0

    def test_cache_invalid_max_size(self):
        """Test max_size invalido solleva errore"""
        with pytest.raises(ValueError, match="max_size deve essere > 0"):
            LRUCache[str](max_size=0)

    def test_set_and_get(self):
        """Test set e get base"""
        cache = LRUCache[str](max_size=10)
        cache.set("key1", "value1")

        result = cache.get("key1")
        assert result == "value1"
        assert cache.stats.hits == 1
        assert cache.stats.misses == 0

    def test_get_nonexistent_key(self):
        """Test get con chiave inesistente"""
        cache = LRUCache[str](max_size=10)
        result = cache.get("nonexistent")

        assert result is None
        assert cache.stats.misses == 1

    def test_set_updates_existing_key(self):
        """Test set aggiorna chiave esistente"""
        cache = LRUCache[str](max_size=10)
        cache.set("key", "value1")
        cache.set("key", "value2")

        result = cache.get("key")
        assert result == "value2"
        assert cache.size() == 1  # Non duplica

    def test_lru_eviction(self):
        """Test eviction LRU quando cache piena"""
        cache = LRUCache[str](max_size=3)

        # Riempi cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Aggiungi quarto elemento - dovrebbe evitare key1 (oldest)
        cache.set("key4", "value4")

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
        assert cache.stats.evictions == 1

    def test_lru_with_access_pattern(self):
        """Test LRU considera accessi recenti"""
        cache = LRUCache[str](max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Accedi a key1 per renderla "recently used"
        _ = cache.get("key1")

        # Aggiungi key4 - dovrebbe evitare key2 (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"  # Ancora presente
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_ttl_expiration(self):
        """Test scadenza TTL"""
        cache = LRUCache[str](max_size=10)
        cache.set("key", "value", ttl=0.1)

        # Valore presente subito
        assert cache.get("key") == "value"

        # Attendi scadenza
        time.sleep(0.15)

        # Valore scaduto
        result = cache.get("key")
        assert result is None
        assert cache.stats.expirations == 1

    def test_default_ttl(self):
        """Test TTL default applicato"""
        cache = LRUCache[str](max_size=10, default_ttl=0.1)
        cache.set("key", "value")  # Usa default TTL

        assert cache.get("key") == "value"
        time.sleep(0.15)
        assert cache.get("key") is None

    def test_ttl_override(self):
        """Test override TTL default"""
        cache = LRUCache[str](max_size=10, default_ttl=0.1)
        cache.set("key", "value", ttl=10.0)  # Override con TTL lungo

        time.sleep(0.15)
        # Non dovrebbe essere scaduto (TTL override)
        assert cache.get("key") == "value"

    def test_delete_existing_key(self):
        """Test delete chiave esistente"""
        cache = LRUCache[str](max_size=10)
        cache.set("key", "value")

        result = cache.delete("key")
        assert result is True
        assert cache.get("key") is None

    def test_delete_nonexistent_key(self):
        """Test delete chiave inesistente"""
        cache = LRUCache[str](max_size=10)
        result = cache.delete("nonexistent")
        assert result is False

    def test_clear(self):
        """Test clear cache"""
        cache = LRUCache[str](max_size=10)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.size() == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cleanup_expired(self):
        """Test cleanup entry scadute"""
        cache = LRUCache[str](max_size=10)
        cache.set("key1", "value1", ttl=0.1)  # Scade
        cache.set("key2", "value2", ttl=10.0)  # Non scade
        cache.set("key3", "value3")  # No TTL

        time.sleep(0.15)

        removed = cache.cleanup_expired()

        assert removed == 1
        assert cache.size() == 2
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_get_stats(self):
        """Test get_stats completo"""
        cache = LRUCache[str](max_size=100, default_ttl=3600)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        _ = cache.get("key1")  # Hit
        _ = cache.get("nonexistent")  # Miss

        stats = cache.get_stats()

        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['current_size'] == 2
        assert stats['max_size'] == 100
        assert stats['utilization_pct'] == 2.0
        assert stats['default_ttl_seconds'] == 3600

    def test_reset_stats(self):
        """Test reset statistiche mantiene cache"""
        cache = LRUCache[str](max_size=10)
        cache.set("key", "value")
        _ = cache.get("key")

        cache.reset_stats()

        assert cache.stats.hits == 0
        assert cache.stats.misses == 0
        assert cache.get("key") == "value"  # Cache mantiene dati

    def test_thread_safety(self):
        """Test thread safety con accessi concorrenti"""
        cache = LRUCache[int](max_size=1000)
        errors = []

        def worker(worker_id: int):
            try:
                for i in range(100):
                    cache.set(f"key_{worker_id}_{i}", i)
                    _ = cache.get(f"key_{worker_id}_{i}")
            except Exception as e:
                errors.append(e)

        # Lancia 10 thread concorrenti
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Non dovrebbero esserci errori
        assert len(errors) == 0
        assert cache.stats.hits > 0

    def test_different_types(self):
        """Test cache con tipi diversi"""
        # String cache
        str_cache = LRUCache[str](max_size=10)
        str_cache.set("key", "value")
        assert str_cache.get("key") == "value"

        # Int cache
        int_cache = LRUCache[int](max_size=10)
        int_cache.set("key", 42)
        assert int_cache.get("key") == 42

        # Dict cache
        dict_cache = LRUCache[dict](max_size=10)
        dict_cache.set("key", {"nested": "value"})
        assert dict_cache.get("key") == {"nested": "value"}


class TestCachedDecorator:
    """Test per decorator @cached"""

    def test_cached_decorator_basic(self):
        """Test decorator base"""
        call_count = 0
        cache = LRUCache[str](max_size=10)

        @cached(cache, key_func=lambda x: x)
        def expensive_func(arg: str) -> str:
            nonlocal call_count
            call_count += 1
            return f"result_{arg}"

        # Prima chiamata - miss
        result1 = expensive_func("test")
        assert result1 == "result_test"
        assert call_count == 1

        # Seconda chiamata - hit (non ricalcola)
        result2 = expensive_func("test")
        assert result2 == "result_test"
        assert call_count == 1  # Non incrementato

        assert cache.stats.hits == 1
        assert cache.stats.misses == 1

    def test_cached_decorator_different_args(self):
        """Test decorator con argomenti diversi"""
        cache = LRUCache[int](max_size=10)

        @cached(cache, key_func=lambda x: str(x))
        def multiply(x: int) -> int:
            return x * 2

        result1 = multiply(5)
        result2 = multiply(10)
        result3 = multiply(5)  # Cache hit

        assert result1 == 10
        assert result2 == 20
        assert result3 == 10

        assert cache.stats.hits == 1
        assert cache.stats.misses == 2

    def test_cached_decorator_with_ttl(self):
        """Test decorator con TTL"""
        cache = LRUCache[str](max_size=10)

        @cached(cache, key_func=lambda x: x, ttl=0.1)
        def func(arg: str) -> str:
            return f"value_{arg}"

        result1 = func("test")
        assert result1 == "value_test"

        # Attendi scadenza
        time.sleep(0.15)

        result2 = func("test")
        assert result2 == "value_test"

        # Dovrebbe aver ricalcolato dopo scadenza
        assert cache.stats.misses == 2  # 2 miss per scadenza

    def test_cached_decorator_default_key(self):
        """Test decorator con key function default"""
        cache = LRUCache[str](max_size=10)
        call_count = 0

        @cached(cache)
        def func(a: int, b: str) -> str:
            nonlocal call_count
            call_count += 1
            return f"{a}_{b}"

        # Chiamate con stessi args
        result1 = func(1, "test")
        result2 = func(1, "test")

        assert result1 == result2 == "1_test"
        assert call_count == 1  # Cache hit sulla seconda

        # Chiamata con args diversi
        result3 = func(2, "other")
        assert result3 == "2_other"
        assert call_count == 2


class TestGlobalCaches:
    """Test per istanze cache globali"""

    def test_url_cache_exists(self):
        """Test url_cache globale esiste"""
        from pyprestascan.core.cache import url_cache
        assert url_cache is not None
        assert url_cache.max_size == 10000

    def test_parse_cache_exists(self):
        """Test parse_cache globale esiste"""
        from pyprestascan.core.cache import parse_cache
        assert parse_cache is not None
        assert parse_cache.max_size == 1000
        assert parse_cache.default_ttl == 3600

    def test_prestashop_cache_exists(self):
        """Test prestashop_cache globale esiste"""
        from pyprestascan.core.cache import prestashop_cache
        assert prestashop_cache is not None
        assert prestashop_cache.max_size == 500
