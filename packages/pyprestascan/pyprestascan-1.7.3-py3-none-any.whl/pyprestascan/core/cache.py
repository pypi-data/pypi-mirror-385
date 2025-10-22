"""
Enterprise caching layer con LRU e TTL support

Features:
- LRU (Least Recently Used) eviction policy
- TTL (Time To Live) per singole voci
- Thread-safe per uso concorrente
- Statistiche per monitoring (hit/miss rate)
- Memory-bounded con max size configurabile
"""
import time
import threading
from typing import Any, Optional, Dict, Tuple, TypeVar, Generic, Callable
from collections import OrderedDict
from dataclasses import dataclass, field
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheEntry(Generic[T]):
    """Voce cache con timestamp e TTL"""
    value: T
    created_at: float = field(default_factory=time.time)
    ttl_seconds: Optional[float] = None

    def is_expired(self) -> bool:
        """Verifica se entry è scaduta"""
        if self.ttl_seconds is None:
            return False
        return (time.time() - self.created_at) > self.ttl_seconds


@dataclass
class CacheStats:
    """Statistiche utilizzo cache"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0

    @property
    def hit_rate(self) -> float:
        """Calcola hit rate percentuale"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100

    @property
    def total_requests(self) -> int:
        """Totale richieste cache"""
        return self.hits + self.misses

    def to_dict(self) -> Dict[str, Any]:
        """Esporta statistiche come dict"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'expirations': self.expirations,
            'hit_rate_pct': round(self.hit_rate, 2),
            'total_requests': self.total_requests
        }


class LRUCache(Generic[T]):
    """
    LRU Cache thread-safe con TTL support

    Features:
    - LRU eviction quando raggiunge max_size
    - TTL per entry (opzionale)
    - Thread-safe con RLock
    - Statistiche dettagliate

    Usage:
        cache = LRUCache[str](max_size=1000, default_ttl=3600)
        cache.set("key", "value")
        value = cache.get("key")
    """

    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        """
        Inizializza LRU cache

        Args:
            max_size: Numero massimo entry nella cache
            default_ttl: TTL default in secondi (None = nessuna scadenza)
        """
        if max_size <= 0:
            raise ValueError("max_size deve essere > 0")

        self.max_size = max_size
        self.default_ttl = default_ttl

        # OrderedDict mantiene ordine inserimento per LRU
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._lock = threading.RLock()
        self.stats = CacheStats()

    def get(self, key: str) -> Optional[T]:
        """
        Recupera valore dalla cache

        Args:
            key: Chiave cache

        Returns:
            Valore se presente e non scaduto, None altrimenti
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self.stats.misses += 1
                return None

            # Verifica scadenza
            if entry.is_expired():
                self.stats.misses += 1
                self.stats.expirations += 1
                # Rimuovi entry scaduta
                del self._cache[key]
                logger.debug(f"Cache entry expired: {key}")
                return None

            # Hit! Sposta in fondo per LRU (most recently used)
            self._cache.move_to_end(key)
            self.stats.hits += 1
            return entry.value

    def set(self, key: str, value: T, ttl: Optional[float] = None) -> None:
        """
        Inserisce valore nella cache

        Args:
            key: Chiave cache
            value: Valore da cachare
            ttl: TTL in secondi (override default_ttl, None = usa default)
        """
        with self._lock:
            # Usa TTL fornito o default
            effective_ttl = ttl if ttl is not None else self.default_ttl

            # Se chiave esiste già, aggiorna
            if key in self._cache:
                self._cache[key] = CacheEntry(value, ttl_seconds=effective_ttl)
                self._cache.move_to_end(key)
                return

            # Eviction se cache piena
            if len(self._cache) >= self.max_size:
                # Rimuovi oldest (primo elemento)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self.stats.evictions += 1
                logger.debug(f"Cache evicted (LRU): {oldest_key}")

            # Inserisci nuovo entry
            self._cache[key] = CacheEntry(value, ttl_seconds=effective_ttl)

    def delete(self, key: str) -> bool:
        """
        Rimuove entry dalla cache

        Args:
            key: Chiave da rimuovere

        Returns:
            True se rimossa, False se non esistente
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Svuota completamente la cache"""
        with self._lock:
            self._cache.clear()
            logger.debug("Cache cleared completely")

    def size(self) -> int:
        """Ritorna numero entry correnti"""
        with self._lock:
            return len(self._cache)

    def cleanup_expired(self) -> int:
        """
        Rimuove tutte le entry scadute

        Returns:
            Numero entry rimosse
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                self.stats.expirations += len(expired_keys)
                logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Ritorna statistiche cache con info correnti"""
        with self._lock:
            stats_dict = self.stats.to_dict()
            stats_dict.update({
                'current_size': len(self._cache),
                'max_size': self.max_size,
                'utilization_pct': round((len(self._cache) / self.max_size) * 100, 2),
                'default_ttl_seconds': self.default_ttl
            })
            return stats_dict

    def reset_stats(self) -> None:
        """Reset statistiche (mantiene cache)"""
        with self._lock:
            self.stats = CacheStats()


def cached(
    cache: LRUCache,
    key_func: Optional[Callable[..., str]] = None,
    ttl: Optional[float] = None
):
    """
    Decorator per cachare risultati funzioni

    Args:
        cache: Istanza LRUCache da usare
        key_func: Funzione per generare cache key da args/kwargs
                  Default: usa str(args) + str(kwargs)
        ttl: TTL override per questa funzione

    Usage:
        url_cache = LRUCache[str](max_size=5000)

        @cached(url_cache, key_func=lambda url: url)
        def normalize_url(url: str) -> str:
            # Expensive normalization...
            return normalized
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Genera cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: usa args + kwargs come key
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Cerca in cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Miss - calcola valore
            result = func(*args, **kwargs)

            # Salva in cache
            cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


# Istanze globali cache per moduli comuni
# (possono essere importate e usate direttamente)

# Cache per URL normalization (molto frequente, no scadenza)
url_cache = LRUCache[str](max_size=10000, default_ttl=None)

# Cache per HTML parsing results (TTL 1 ora)
parse_cache = LRUCache[Any](max_size=1000, default_ttl=3600)

# Cache per rilevamento PrestaShop (no scadenza, small size)
prestashop_cache = LRUCache[Dict](max_size=500, default_ttl=None)


# Export
__all__ = [
    'CacheEntry',
    'CacheStats',
    'LRUCache',
    'cached',
    'url_cache',
    'parse_cache',
    'prestashop_cache'
]
