"""
Database connection pooling per enterprise scalability
"""
import asyncio
import aiosqlite
from pathlib import Path
from typing import Optional, AsyncIterator
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseConnectionPool:
    """
    Connection pool per aiosqlite con gestione automatica connessioni

    Features:
    - Pool size configurabile
    - Timeout configurable
    - Health checks automatici
    - Graceful shutdown
    """

    def __init__(self, db_path: Path, pool_size: int = 5, timeout: float = 10.0):
        """
        Inizializza connection pool

        Args:
            db_path: Path al database SQLite
            pool_size: Numero massimo connessioni nel pool
            timeout: Timeout in secondi per acquisire connessione
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout

        # Queue per connessioni disponibili
        self._pool: asyncio.Queue[aiosqlite.Connection] = asyncio.Queue(maxsize=pool_size)
        self._all_connections: list[aiosqlite.Connection] = []
        self._initialized = False
        self._closed = False

        # Statistiche
        self.stats = {
            'total_acquired': 0,
            'total_released': 0,
            'current_in_use': 0,
            'pool_exhausted_count': 0
        }

    async def initialize(self) -> None:
        """Inizializza pool creando connessioni"""
        if self._initialized:
            return

        logger.info(f"📊 Inizializzo DB pool: {self.pool_size} connessioni per {self.db_path}")

        for i in range(self.pool_size):
            try:
                conn = await aiosqlite.connect(self.db_path)
                # Abilita WAL mode per migliori performance concorrenti
                await conn.execute("PRAGMA journal_mode=WAL")
                # Ottimizzazioni
                await conn.execute("PRAGMA synchronous=NORMAL")
                await conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
                await conn.execute("PRAGMA temp_store=MEMORY")

                self._all_connections.append(conn)
                await self._pool.put(conn)
                logger.debug(f"✅ Connessione pool #{i+1} creata")
            except Exception as e:
                logger.error(f"❌ Errore creazione connessione pool #{i+1}: {e}")
                raise

        self._initialized = True
        logger.info(f"✅ DB pool inizializzato: {self.pool_size} connessioni pronte")

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[aiosqlite.Connection]:
        """
        Acquisisce connessione dal pool (context manager)

        Usage:
            async with pool.acquire() as conn:
                await conn.execute("SELECT * FROM pages")

        Yields:
            aiosqlite.Connection

        Raises:
            asyncio.TimeoutError: Se timeout acquisizione
            RuntimeError: Se pool non inizializzato
        """
        if not self._initialized:
            raise RuntimeError("Pool non inizializzato. Chiamare initialize() prima.")

        if self._closed:
            raise RuntimeError("Pool chiuso. Non è possibile acquisire connessioni.")

        conn = None
        try:
            # Acquisici connessione con timeout
            try:
                conn = await asyncio.wait_for(self._pool.get(), timeout=self.timeout)
            except asyncio.TimeoutError:
                self.stats['pool_exhausted_count'] += 1
                logger.warning(
                    f"⚠️ Pool esaurito! Timeout {self.timeout}s acquisizione connessione. "
                    f"In uso: {self.stats['current_in_use']}/{self.pool_size}"
                )
                raise

            self.stats['total_acquired'] += 1
            self.stats['current_in_use'] += 1

            # Verifica health connessione
            try:
                await conn.execute("SELECT 1")
            except Exception as e:
                logger.warning(f"⚠️ Connessione non sana, ricreo: {e}")
                await conn.close()
                conn = await aiosqlite.connect(self.db_path)
                await conn.execute("PRAGMA journal_mode=WAL")

            yield conn

        finally:
            # Rilascia connessione nel pool
            if conn:
                self.stats['total_released'] += 1
                self.stats['current_in_use'] -= 1
                try:
                    await self._pool.put(conn)
                except Exception as e:
                    logger.error(f"❌ Errore rilascio connessione: {e}")

    async def close(self) -> None:
        """Chiude tutte le connessioni del pool"""
        if self._closed:
            return

        logger.info(f"🔒 Chiudo DB pool ({len(self._all_connections)} connessioni)...")

        self._closed = True

        # Chiudi tutte le connessioni
        for i, conn in enumerate(self._all_connections):
            try:
                await conn.close()
                logger.debug(f"✅ Connessione #{i+1} chiusa")
            except Exception as e:
                logger.error(f"❌ Errore chiusura connessione #{i+1}: {e}")

        self._all_connections.clear()

        # Svuota queue
        while not self._pool.empty():
            try:
                self._pool.get_nowait()
            except asyncio.QueueEmpty:
                break

        logger.info("✅ DB pool chiuso completamente")
        logger.info(f"📊 Statistiche finali: {self.stats}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    def get_stats(self) -> dict:
        """Ritorna statistiche utilizzo pool"""
        return {
            **self.stats,
            'pool_size': self.pool_size,
            'available': self._pool.qsize(),
            'utilization_pct': (self.stats['current_in_use'] / self.pool_size) * 100
        }


# Export
__all__ = ['DatabaseConnectionPool']
