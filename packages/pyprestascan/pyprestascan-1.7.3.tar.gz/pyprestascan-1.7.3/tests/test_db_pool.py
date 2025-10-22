"""
Test per database connection pool
"""
import pytest
import asyncio
from pathlib import Path
import tempfile

from pyprestascan.core.db_pool import DatabaseConnectionPool


class TestDatabaseConnectionPool:
    """Test per DatabaseConnectionPool"""

    @pytest.mark.asyncio
    async def test_pool_initialization(self):
        """Test inizializzazione pool"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        try:
            pool = DatabaseConnectionPool(db_path, pool_size=3)
            await pool.initialize()

            assert pool._initialized is True
            assert len(pool._all_connections) == 3
            assert pool._pool.qsize() == 3

            await pool.close()
        finally:
            db_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_acquire_release(self):
        """Test acquisizione e rilascio connessione"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        try:
            pool = DatabaseConnectionPool(db_path, pool_size=2)
            await pool.initialize()

            # Acquisici connessione
            async with pool.acquire() as conn:
                # Verifica che funzioni
                cursor = await conn.execute("SELECT 1")
                result = await cursor.fetchone()
                assert result == (1,)

            # Verifica che sia stata rilasciata
            assert pool.stats['total_acquired'] == 1
            assert pool.stats['total_released'] == 1
            assert pool.stats['current_in_use'] == 0

            await pool.close()
        finally:
            db_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_multiple_acquisitions(self):
        """Test acquisizioni multiple concorrenti"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        try:
            pool = DatabaseConnectionPool(db_path, pool_size=3)
            await pool.initialize()

            # Acquisisci 3 connessioni in parallelo
            async def use_connection(conn_id: int):
                async with pool.acquire() as conn:
                    await conn.execute(
                        "CREATE TABLE IF NOT EXISTS test (id INTEGER, value TEXT)"
                    )
                    await conn.execute(f"INSERT INTO test VALUES ({conn_id}, 'test')")
                    await conn.commit()
                    await asyncio.sleep(0.1)  # Simula lavoro

            tasks = [use_connection(i) for i in range(3)]
            await asyncio.gather(*tasks)

            # Verifica statistiche
            assert pool.stats['total_acquired'] == 3
            assert pool.stats['total_released'] == 3
            assert pool.stats['current_in_use'] == 0

            await pool.close()
        finally:
            db_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_pool_exhaustion(self):
        """Test esaurimento pool con timeout"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        try:
            pool = DatabaseConnectionPool(db_path, pool_size=1, timeout=0.5)
            await pool.initialize()

            # Acquisisci l'unica connessione
            async with pool.acquire() as conn1:
                # Prova ad acquisire seconda connessione (dovrebbe timeout)
                with pytest.raises(asyncio.TimeoutError):
                    async with pool.acquire() as conn2:
                        pass

            # Verifica che il pool exhausted sia stato contato
            assert pool.stats['pool_exhausted_count'] == 1

            await pool.close()
        finally:
            db_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        try:
            async with DatabaseConnectionPool(db_path, pool_size=2) as pool:
                async with pool.acquire() as conn:
                    cursor = await conn.execute("SELECT 1")
                    result = await cursor.fetchone()
                    assert result == (1,)

            # Pool dovrebbe essere chiuso
            assert pool._closed is True
        finally:
            db_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_stats(self):
        """Test statistiche pool"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        try:
            pool = DatabaseConnectionPool(db_path, pool_size=2)
            await pool.initialize()

            stats = pool.get_stats()
            assert stats['pool_size'] == 2
            assert stats['available'] == 2
            assert stats['current_in_use'] == 0
            assert stats['utilization_pct'] == 0

            async with pool.acquire() as conn:
                stats_in_use = pool.get_stats()
                assert stats_in_use['current_in_use'] == 1
                assert stats_in_use['available'] == 1
                assert stats_in_use['utilization_pct'] == 50.0

            await pool.close()
        finally:
            db_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_error_handling_not_initialized(self):
        """Test errore se pool non inizializzato"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        try:
            pool = DatabaseConnectionPool(db_path, pool_size=1)
            # Non chiamiamo initialize()

            with pytest.raises(RuntimeError, match="non inizializzato"):
                async with pool.acquire() as conn:
                    pass
        finally:
            db_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_error_handling_closed_pool(self):
        """Test errore se pool chiuso"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        try:
            pool = DatabaseConnectionPool(db_path, pool_size=1)
            await pool.initialize()
            await pool.close()

            # Prova ad acquisire dopo close
            with pytest.raises(RuntimeError, match="Pool chiuso"):
                async with pool.acquire() as conn:
                    pass
        finally:
            db_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_concurrent_load(self):
        """Test carico concorrente pesante"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        try:
            pool = DatabaseConnectionPool(db_path, pool_size=5)
            await pool.initialize()

            # Crea tabella
            async with pool.acquire() as conn:
                await conn.execute(
                    "CREATE TABLE IF NOT EXISTS load_test (id INTEGER PRIMARY KEY, value TEXT)"
                )
                await conn.commit()

            # 20 task concorrenti che usano 5 connessioni
            async def write_data(task_id: int):
                for i in range(10):
                    async with pool.acquire() as conn:
                        await conn.execute(
                            f"INSERT INTO load_test (value) VALUES ('task_{task_id}_iter_{i}')"
                        )
                        await conn.commit()

            tasks = [write_data(i) for i in range(20)]
            await asyncio.gather(*tasks)

            # Verifica che siano stati inseriti 200 record
            async with pool.acquire() as conn:
                cursor = await conn.execute("SELECT COUNT(*) FROM load_test")
                count = await cursor.fetchone()
                assert count[0] == 200

            # Verifica statistiche (1 CREATE + 200 inserts + 1 SELECT)
            assert pool.stats['total_acquired'] == 202
            assert pool.stats['total_released'] == 202
            assert pool.stats['current_in_use'] == 0

            await pool.close()
        finally:
            db_path.unlink(missing_ok=True)
