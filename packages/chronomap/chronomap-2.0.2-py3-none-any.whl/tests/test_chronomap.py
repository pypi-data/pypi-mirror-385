"""
Comprehensive unit tests for ChronoMap.

Run with: pytest test_chronomap.py -v
Coverage: pytest test_chronomap.py --cov=chronomap --cov-report=html
"""

import pytest
import time
import json
import pickle
import tempfile
import threading
from pathlib import Path
from chronomap import (
    ChronoMap,
    ChronoMapError,
    ChronoMapKeyError,
    ChronoMapTypeError,
    ChronoMapValueError,
)


# ============================================================================
# Basic Operations Tests
# ============================================================================

class TestBasicOperations:
    """Test core put, get, delete operations."""

    def test_put_and_get(self):
        cm = ChronoMap()
        cm.put('key', 'value')
        assert cm.get('key') == 'value'

    def test_put_with_timestamp(self):
        cm = ChronoMap()
        cm.put('key', 'value1', timestamp=100)
        cm.put('key', 'value2', timestamp=200)
        assert cm.get('key', timestamp=150) == 'value1'
        assert cm.get('key', timestamp=250) == 'value2'

    def test_get_default(self):
        cm = ChronoMap()
        assert cm.get('nonexistent', default='default') == 'default'

    def test_get_strict_raises(self):
        cm = ChronoMap()
        with pytest.raises(ChronoMapKeyError):
            cm.get('nonexistent', strict=True)

    def test_delete(self):
        cm = ChronoMap()
        cm.put('key', 'value')
        assert cm.delete('key') is True
        assert cm.delete('key') is False
        assert 'key' not in cm

    def test_empty_map(self):
        cm = ChronoMap()
        assert len(cm) == 0
        assert not cm
        assert list(cm.keys()) == []


# ============================================================================
# TTL / Expiry Tests
# ============================================================================

class TestTTL:
    """Test TTL and key expiration."""

    def test_ttl_expiry(self):
        cm = ChronoMap()
        cm.put('temp', 'value', ttl=0.1)
        assert cm.get('temp') == 'value'
        time.sleep(0.15)
        assert cm.get('temp') is None

    def test_ttl_strict_raises(self):
        cm = ChronoMap()
        cm.put('temp', 'value', ttl=0.1)
        time.sleep(0.15)
        with pytest.raises(ChronoMapKeyError):
            cm.get('temp', strict=True)

    def test_ttl_contains(self):
        cm = ChronoMap()
        cm.put('temp', 'value', ttl=0.1)
        assert 'temp' in cm
        time.sleep(0.15)
        assert 'temp' not in cm

    def test_ttl_negative_raises(self):
        cm = ChronoMap()
        with pytest.raises(ChronoMapValueError):
            cm.put('key', 'value', ttl=-1)

    def test_clean_expired_keys(self):
        cm = ChronoMap()
        cm.put('temp1', 'v1', ttl=0.1)
        cm.put('temp2', 'v2', ttl=0.1)
        cm.put('perm', 'v3')
        time.sleep(0.15)
        removed = cm.clean_expired_keys()
        assert removed == 2
        assert 'perm' in cm


# ============================================================================
# Batch Operations Tests
# ============================================================================

class TestBatchOperations:
    """Test batch put and delete operations."""

    def test_put_many(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2, 'c': 3})
        assert cm['a'] == 1
        assert cm['b'] == 2
        assert cm['c'] == 3

    def test_put_many_with_ttl(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2}, ttl=0.1)
        assert cm['a'] == 1
        time.sleep(0.15)
        assert cm.get('a') is None

    def test_delete_many(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2, 'c': 3})
        deleted = cm.delete_many(['a', 'b', 'nonexistent'])
        assert deleted == 2
        assert 'a' not in cm
        assert 'b' not in cm
        assert 'c' in cm


# ============================================================================
# Advanced Query Tests
# ============================================================================

class TestAdvancedQueries:
    """Test range queries and latest keys."""

    def test_get_range(self):
        cm = ChronoMap()
        cm.put('temp', 20, timestamp=100)
        cm.put('temp', 22, timestamp=200)
        cm.put('temp', 24, timestamp=300)
        
        result = cm.get_range('temp', start_ts=150, end_ts=250)
        assert len(result) == 1
        assert result[0] == (200, 22)

    def test_get_range_all(self):
        cm = ChronoMap()
        cm.put('temp', 20, timestamp=100)
        cm.put('temp', 22, timestamp=200)
        
        result = cm.get_range('temp')
        assert len(result) == 2

    def test_get_latest_keys(self):
        cm = ChronoMap()
        cm.put('a', 1, timestamp=100)
        cm.put('b', 2, timestamp=200)
        cm.put('c', 3, timestamp=300)
        
        latest = cm.get_latest_keys(2)
        assert len(latest) == 2
        assert latest[0][0] == 'c'  # Most recent
        assert latest[1][0] == 'b'

    def test_get_keys_by_value(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 1, 'c': 2})
        keys = cm.get_keys_by_value(1)
        assert set(keys) == {'a', 'b'}


# ============================================================================
# Snapshot, Diff, Rollback Tests
# ============================================================================

class TestSnapshotDiffRollback:
    """Test snapshot, diff, and rollback functionality."""

    def test_snapshot(self):
        cm = ChronoMap()
        cm['key'] = 'value1'
        snap = cm.snapshot()
        cm['key'] = 'value2'
        assert cm['key'] == 'value2'
        assert snap['key'] == 'value1'

    def test_rollback(self):
        cm = ChronoMap()
        cm['key'] = 'value1'
        snap = cm.snapshot()
        cm['key'] = 'value2'
        cm['new_key'] = 'new_value'
        cm.rollback(snap)
        assert cm['key'] == 'value1'
        assert 'new_key' not in cm

    def test_rollback_invalid_type(self):
        cm = ChronoMap()
        with pytest.raises(ChronoMapTypeError):
            cm.rollback({'not': 'a chronomap'})

    def test_diff(self):
        cm1 = ChronoMap()
        cm2 = ChronoMap()
        cm1.put_many({'a': 1, 'b': 2})
        cm2.put_many({'a': 1, 'b': 3, 'c': 4})
        
        diff = cm1.diff(cm2)
        assert 'b' in diff  # Different value
        assert 'c' in diff  # Only in cm2

    def test_diff_detailed(self):
        cm1 = ChronoMap()
        cm2 = ChronoMap()
        cm1['a'] = 1
        cm2['a'] = 2
        
        changes = cm1.diff_detailed(cm2)
        assert len(changes) == 1
        assert changes[0] == ('a', 2, 1)


# ============================================================================
# Merge Tests
# ============================================================================

class TestMerge:
    """Test merge functionality."""

    def test_merge_timestamp_strategy(self):
        cm1 = ChronoMap()
        cm2 = ChronoMap()
        cm1.put('a', 1, timestamp=100)
        cm2.put('a', 2, timestamp=200)
        
        cm1.merge(cm2, strategy='timestamp')
        history = cm1.history('a')
        assert len(history) == 2
        assert history[0] == (100, 1)
        assert history[1] == (200, 2)

    def test_merge_overwrite_strategy(self):
        cm1 = ChronoMap()
        cm2 = ChronoMap()
        cm1.put('a', 1, timestamp=100)
        cm2.put('a', 2, timestamp=200)
        
        cm1.merge(cm2, strategy='overwrite')
        assert cm1['a'] == 2

    def test_merge_invalid_strategy(self):
        cm1 = ChronoMap()
        cm2 = ChronoMap()
        with pytest.raises(ChronoMapValueError):
            cm1.merge(cm2, strategy='invalid')

    def test_merge_invalid_type(self):
        cm = ChronoMap()
        with pytest.raises(ChronoMapTypeError):
            cm.merge({'not': 'a chronomap'})


# ============================================================================
# Magic Methods Tests
# ============================================================================

class TestMagicMethods:
    """Test Pythonic magic methods."""

    def test_getitem(self):
        cm = ChronoMap()
        cm.put('key', 'value')
        assert cm['key'] == 'value'

    def test_getitem_raises(self):
        cm = ChronoMap()
        with pytest.raises(ChronoMapKeyError):
            _ = cm['nonexistent']

    def test_setitem(self):
        cm = ChronoMap()
        cm['key'] = 'value'
        assert cm.get('key') == 'value'

    def test_delitem(self):
        cm = ChronoMap()
        cm['key'] = 'value'
        del cm['key']
        assert 'key' not in cm

    def test_delitem_raises(self):
        cm = ChronoMap()
        with pytest.raises(ChronoMapKeyError):
            del cm['nonexistent']

    def test_len(self):
        cm = ChronoMap()
        assert len(cm) == 0
        cm.put_many({'a': 1, 'b': 2, 'c': 3})
        assert len(cm) == 3

    def test_contains(self):
        cm = ChronoMap()
        cm['key'] = 'value'
        assert 'key' in cm
        assert 'nonexistent' not in cm

    def test_bool(self):
        cm = ChronoMap()
        assert not cm
        cm['key'] = 'value'
        assert cm

    def test_eq(self):
        cm1 = ChronoMap()
        cm2 = ChronoMap()
        cm1.put_many({'a': 1, 'b': 2})
        cm2.put_many({'a': 1, 'b': 2})
        assert cm1 == cm2
        
        cm2['b'] = 3
        assert cm1 != cm2

    def test_iter(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2, 'c': 3})
        keys = list(cm)
        assert set(keys) == {'a', 'b', 'c'}


# ============================================================================
# Iteration Tests
# ============================================================================

class TestIteration:
    """Test iteration methods."""

    def test_keys(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2})
        assert set(cm.keys()) == {'a', 'b'}

    def test_values(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2})
        assert set(cm.values()) == {1, 2}

    def test_items(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2})
        assert set(cm.items()) == {('a', 1), ('b', 2)}

    def test_iter_history(self):
        cm = ChronoMap()
        cm.put('key', 'v1', timestamp=100)
        cm.put('key', 'v2', timestamp=200)
        
        history = list(cm.iter_history('key'))
        assert len(history) == 2
        assert history[0] == (100, 'v1')
        assert history[1] == (200, 'v2')


# ============================================================================
# Utility Methods Tests
# ============================================================================

class TestUtilityMethods:
    """Test utility methods."""

    def test_latest(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2})
        assert cm.latest() == {'a': 1, 'b': 2}

    def test_history(self):
        cm = ChronoMap()
        cm.put('key', 'v1', timestamp=100)
        cm.put('key', 'v2', timestamp=200)
        
        history = cm.history('key')
        assert len(history) == 2
        assert history[0] == (100, 'v1')

    def test_clear(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2})
        cm.clear()
        assert len(cm) == 0
        assert cm.latest() == {}

    def test_repr(self):
        cm = ChronoMap()
        cm['key'] = 'value'
        repr_str = repr(cm)
        assert 'ChronoMap' in repr_str
        assert 'key' in repr_str


# ============================================================================
# Validation Tests
# ============================================================================

class TestValidation:
    """Test input validation."""

    def test_unhashable_key_raises(self):
        cm = ChronoMap()
        with pytest.raises(ChronoMapTypeError):
            cm.put(['unhashable', 'list'], 'value')

    def test_invalid_timestamp_type_raises(self):
        cm = ChronoMap()
        with pytest.raises(ChronoMapTypeError):
            cm.put('key', 'value', timestamp='not a number')

    def test_invalid_timestamp_value_raises(self):
        cm = ChronoMap()
        with pytest.raises(ChronoMapValueError):
            cm.put('key', 'value', timestamp=float('inf'))


# ============================================================================
# Persistence Tests
# ============================================================================

class TestPersistence:
    """Test serialization and persistence."""

    def test_to_dict_from_dict(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2})
        
        data = cm.to_dict()
        cm2 = ChronoMap.from_dict(data)
        
        assert cm2['a'] == 1
        assert cm2['b'] == 2

    def test_save_load_json(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2})
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'test.json'
            cm.save_json(filepath)
            cm2 = ChronoMap.load_json(filepath)
            
            assert cm2['a'] == 1
            assert cm2['b'] == 2

    def test_save_load_pickle(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2, 'c': [1, 2, 3]})
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'test.pkl'
            cm.save_pickle(filepath)
            cm2 = ChronoMap.load_pickle(filepath)
            
            assert cm2['a'] == 1
            assert cm2['c'] == [1, 2, 3]


# ============================================================================
# Thread Safety Tests
# ============================================================================

class TestThreadSafety:
    """Test thread safety of operations."""

    def test_concurrent_puts(self):
        cm = ChronoMap()
        
        def put_values(start, count):
            for i in range(start, start + count):
                cm.put(f'key{i}', i)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=put_values, args=(i*100, 100))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(cm) == 500

    def test_concurrent_reads_writes(self):
        cm = ChronoMap()
        cm.put_many({f'key{i}': i for i in range(100)})
        
        results = []
        
        def reader():
            for _ in range(100):
                results.append(cm.get('key50'))
        
        def writer():
            for i in range(100):
                cm.put('key50', i)
        
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=reader))
            threads.append(threading.Thread(target=writer))
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should complete without errors
        assert len(results) > 0

    def test_concurrent_snapshot_modify(self):
        cm = ChronoMap()
        cm.put_many({'a': 1, 'b': 2})
        
        snapshots = []
        
        def take_snapshot():
            for _ in range(10):
                snapshots.append(cm.snapshot())
                time.sleep(0.001)
        
        def modify():
            for i in range(10):
                cm.put('a', i)
                time.sleep(0.001)
        
        t1 = threading.Thread(target=take_snapshot)
        t2 = threading.Thread(target=modify)
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        assert len(snapshots) == 10


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_put_same_timestamp_multiple_values(self):
        cm = ChronoMap()
        cm.put('key', 'v1', timestamp=100)
        cm.put('key', 'v2', timestamp=100)
        
        # Later put should be retrievable
        assert cm.get('key', timestamp=100) == 'v2'

    def test_get_before_first_timestamp(self):
        cm = ChronoMap()
        cm.put('key', 'value', timestamp=100)
        assert cm.get('key', timestamp=50) is None

    def test_empty_history(self):
        cm = ChronoMap()
        assert cm.history('nonexistent') == []

    def test_delete_nonexistent(self):
        cm = ChronoMap()
        assert cm.delete('nonexistent') is False

    def test_large_history(self):
        cm = ChronoMap()
        for i in range(1000):
            cm.put('key', i, timestamp=i)
        
        history = cm.history('key')
        assert len(history) == 1000
        assert cm.get('key', timestamp=500) == 500

    def test_none_as_value(self):
        cm = ChronoMap()
        cm['key'] = None
        assert cm['key'] is None
        assert 'key' in cm

    def test_complex_objects_as_values(self):
        cm = ChronoMap()
        cm['dict'] = {'nested': {'value': 123}}
        cm['list'] = [1, 2, [3, 4]]
        
        assert cm['dict']['nested']['value'] == 123
        assert cm['list'][2][1] == 4


# ============================================================================
# Debug Mode Tests
# ============================================================================

class TestDebugMode:
    """Test debug logging."""

    def test_debug_mode_enabled(self):
        cm = ChronoMap(debug=True)
        cm.put('key', 'value')
        # Should not raise, just enable logging
        assert cm.get('key') == 'value'


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow(self):
        """Test a complete workflow with multiple features."""
        # Create and populate
        cm = ChronoMap(debug=False)
        cm.put_many({'user1': 'active', 'user2': 'active', 'user3': 'inactive'})
        
        # Take snapshot
        snap1 = cm.snapshot()
        
        # Modify
        cm['user1'] = 'inactive'
        cm['user4'] = 'active'
        
        # Query
        active_users = cm.get_keys_by_value('active')
        assert set(active_users) == {'user2', 'user4'}
        
        # Diff
        changed = cm.diff(snap1)
        assert 'user1' in changed
        assert 'user4' in changed
        
        # Rollback
        cm.rollback(snap1)
        assert cm['user1'] == 'active'
        assert 'user4' not in cm
        
        # Persistence
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'state.pkl'
            cm.save_pickle(filepath)
            cm2 = ChronoMap.load_pickle(filepath)
            assert cm2 == cm

    def test_time_series_scenario(self):
        """Test time-series data scenario."""
        cm = ChronoMap()
        
        # Record temperature readings
        for hour in range(24):
            temp = 20 + (hour % 12)  # Simple pattern
            cm.put('temperature', temp, timestamp=hour * 3600)
        
        # Query range
        morning_temps = cm.get_range('temperature', start_ts=0, end_ts=12*3600)
        assert len(morning_temps) == 13  # 0-12 inclusive
        
        # Get history
        full_history = cm.history('temperature')
        assert len(full_history) == 24

    def test_session_management_scenario(self):
        """Test session management with TTL."""
        cm = ChronoMap()
        
        # Create sessions with 0.2 second TTL
        cm.put('session1', {'user': 'alice'}, ttl=0.2)
        cm.put('session2', {'user': 'bob'}, ttl=0.2)
        cm.put('session3', {'user': 'charlie'}, ttl=0.2)
        
        # All sessions active
        assert len(cm) == 3
        
        # Wait for expiry
        time.sleep(0.25)
        
        # All sessions expired
        assert len(cm) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])