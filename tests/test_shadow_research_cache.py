import sqlite3
import pytest

from shadow_research_cache import ResearchCache


def test_committed_checkpoint_survives_reopen_and_detects_corruption(tmp_path):
    path = tmp_path / 'cache.sqlite'
    with ResearchCache(path) as cache:
        cache.put('observations', 'one', {'value': 10})
    with ResearchCache(path) as cache:
        assert cache.get('observations', 'one') == {'value': 10}
        assert cache.get('other-namespace', 'one') is None
    with sqlite3.connect(path) as connection:
        connection.execute('UPDATE checkpoints SET payload=?', (b'broken',))
    with ResearchCache(path) as cache:
        assert cache.get('observations', 'one') is None


def test_completed_cache_writes_survive_interrupted_context(tmp_path):
    path = tmp_path / 'cache.sqlite'
    with pytest.raises(KeyboardInterrupt):
        with ResearchCache(path) as cache:
            cache.put('stage', 'one', [1, 2])
            raise KeyboardInterrupt()
    with ResearchCache(path) as cache:
        assert cache.get('stage', 'one') == [1, 2]
