# ChronoMap

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-65%20passed-brightgreen.svg)](tests/)
![Logo](https://github.com/Devansh-567/Chronomap/blob/main/Chronomap.png)

**ChronoMap** is a thread-safe, time-versioned key-value store for Python that maintains complete history of all changes. Perfect for configuration management, audit trails, time-series data, and any application requiring historical data tracking.

## ✨ Features

- **⏱️ Time-Versioned Storage** - Every value change is timestamped and preserved
- **🔒 Thread-Safe** - All operations are protected with locks for concurrent access
- **📸 Snapshots & Rollback** - Create snapshots and rollback to any previous state
- **⏰ TTL Support** - Automatic key expiration with time-to-live
- **🔄 Batch Operations** - Efficient `put_many()` and `delete_many()` operations
- **🔍 Advanced Queries** - Range queries, find latest keys, search by value
- **🤝 Merge & Diff** - Merge multiple maps and track differences
- **💾 Persistence** - Save/load from JSON or Pickle
- **🐍 Pythonic API** - Dictionary-like interface with magic methods
- **📝 Comprehensive Testing** - 65 tests with >90% coverage

## 📦 Installation

```bash
pip install chronomap
```

## 🚀 Quick Start

```python
from chronomap import ChronoMap

cm = ChronoMap()
cm['user'] = 'alice'
cm['status'] = 'active'
print(cm['user'])
if 'user' in cm:
    print(f"Found {len(cm)} keys")
for key, value in cm.items():
    print(f"{key}: {value}")
```

## 📚 Documentation

### Basic Operations

```python
cm.put('key', 'value')
value = cm.get('key')
cm.delete('key')

cm['key'] = 'value'
value = cm['key']
del cm['key']

if 'key' in cm:
    print("Key exists")
value = cm.get('nonexistent', default='default_value')

try:
    value = cm.get('nonexistent', strict=True)
except ChronoMapKeyError:
    print("Key not found")
```

### Time-Versioned Storage

```python
cm.put('temperature', 20.5, timestamp=1609459200)
cm.put('temperature', 21.0, timestamp=1609462800)
cm.put('temperature', 22.5, timestamp=1609466400)

temp_at_1am = cm.get('temperature', timestamp=1609462800)
print(temp_at_1am)
latest = cm.get('temperature')
print(latest)
history = cm.history('temperature')
for timestamp, value in cm.iter_history('temperature'):
    print(f"{timestamp}: {value}")
```

### TTL and Auto-Expiry

```python
cm.put('session_token', 'abc123', ttl=3600)
print(cm.get('session_token'))
removed_count = cm.clean_expired_keys()
print(f"Removed {removed_count} expired keys")
```

### Snapshots and Rollback

```python
cm['counter'] = 10
cm['status'] = 'active'
snapshot = cm.snapshot()
cm['counter'] = 100
cm['status'] = 'inactive'
cm['new_key'] = 'new_value'
cm.rollback(snapshot)
print(cm['counter'])
print(cm['status'])
print(cm.get('new_key'))
```

### Batch Operations

```python
users = {
    'user:1': {'name': 'Alice', 'role': 'admin'},
    'user:2': {'name': 'Bob', 'role': 'user'},
    'user:3': {'name': 'Charlie', 'role': 'user'}
}
cm.put_many(users)
cm.put_many(users, ttl=3600)
cm.put_many(users, timestamp=1609459200)
deleted_count = cm.delete_many(['user:2', 'user:3'])
print(f"Deleted {deleted_count} keys")
```

### Advanced Queries

```python
cm.put('sensor', 10, timestamp=100)
cm.put('sensor', 15, timestamp=200)
cm.put('sensor', 20, timestamp=300)
readings = cm.get_range('sensor', start_ts=150, end_ts=250)

latest = cm.get_latest_keys(2)
for key, timestamp, value in latest:
    print(f"{key}: {value} (updated at {timestamp})")

cm.put_many({'user1': 'active', 'user2': 'active', 'user3': 'inactive'})
active_users = cm.get_keys_by_value('active')
```

### Merge and Diff

```python
cm1 = ChronoMap()
cm2 = ChronoMap()
cm1.put('shared', 'v1', timestamp=100)
cm2.put('shared', 'v2', timestamp=200)
cm2.put('unique', 'data')
cm1.merge(cm2, strategy='timestamp')
cm1.merge(cm2, strategy='overwrite')
changed_keys = cm1.diff(cm2)
changes = cm1.diff_detailed(cm2)
for key, old_val, new_val in changes:
    print(f"{key}: {old_val} -> {new_val}")
```

### Persistence

```python
cm.save_json('state.json')
cm_loaded = ChronoMap.load_json('state.json')
cm.save_pickle('state.pkl')
cm_loaded = ChronoMap.load_pickle('state.pkl')
data = cm.to_dict()
cm_restored = ChronoMap.from_dict(data)
```

### Iteration

```python
cm.put_many({'a': 1, 'b': 2, 'c': 3})
for key in cm:
    print(key)
for key in cm.keys():
    print(key)
for value in cm.values():
    print(value)
for key, value in cm.items():
    print(f"{key}: {value}")
latest = cm.latest()
```

### Utility Models

```python
print(len(cm))
if not cm:
    print("Map is empty")
cm.clear()
print(repr(cm))
snap = cm.snapshot()
print(snap.snapshot_time)
```

## 🧪 Testing

```bash
pytest tests/test_chronomap.py -v
pytest tests/test_chronomap.py --cov=chronomap --cov-report=html
pytest tests/test_chronomap.py::TestBasicOperations -v
pytest tests/test_chronomap.py -v -s
```

## Test coverage includes:

- ✅ Basic operations (put, get, delete)
- ✅ TTL and expiry
- ✅ Batch operations
- ✅ Advanced queries
- ✅ Snapshots and rollback
- ✅ Merge and diff
- ✅ Magic methods
- ✅ Iteration
- ✅ Persistence (JSON, Pickle)
- ✅ Thread safety
- ✅ Edge cases
- ✅ Integration scenarios

### Project Structure

```
chronomap/
├── chronomap/
│   ├── __init__.py
│   ├── chronomap.py          # Core implementation
│   └── __main__.py            # CLI interface
├── tests/
│   └── test_chronomap.py      # Test suite
├── examples/
│   ├── config_manager.py
│   ├── session_store.py
│   └── metrics_store.py
├── docs/
│   └── examples.md
├── README.md
├── setup.py
├── pyproject.toml
└── LICENSE
```

### Contributing

1. Fork the repository
2. Write tests for your changes
3. Ensure all tests pass (`pytest tests/ -v`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request
7.

## 📋 Requirements

- Python 3.7+
- No external dependencies for core functionality
- Development dependencies: pytest, pytest-cov

## 🗺️ Roadmap

- [ ] Async/await support
- [ ] SQLite backend for persistence
- [ ] Compression for large histories
- [ ] Query language for complex searches
- [ ] Web UI for visualization
- [ ] Export to various formats (CSV, Parquet)
- [ ] Integration with popular frameworks (Django, Flask)

## 📈 Changelog

### v2.0.0 (2025)

- Complete rewrite with enhanced features
- Added TTL/expiry support
- Added batch operations
- Added advanced queries (range, latest keys, search by value)
- Added merge and diff functionality
- Added comprehensive test suite (65 tests)
- Improved thread safety
- Enhanced documentation

### v1.0.0

- Initial release
- Basic time-versioned storage
- Snapshot and rollback
- Persistence support

## 💡 Tips and Best Practices

1. **Use TTL for temporary data** - Session tokens, cache entries, temporary flags
2. **Take snapshots before risky operations** - Database migrations, bulk updates
3. **Use batch operations** - More efficient than individual operations
4. **Clean expired keys regularly** - Call `clean_expired_keys()` during maintenance
5. **Leverage history for auditing** - Track configuration changes, document versions
6. **Use descriptive key naming** - `user:123:profile` is better than `u123p`
7. **Persist regularly** - Save state periodically using `save_json()` or `save_pickle()`
8. **Monitor map size** - Large histories may need archiving or cleanup

## ❓ FAQ

**Q: Is ChronoMap suitable for production use?**  
A: Yes! ChronoMap is thread-safe, well-tested, and used in production environments.

**Q: How much memory does ChronoMap use?**  
A: Memory usage depends on the number of keys and history size. Each value change is stored, so keys with frequent updates will use more memory.

**Q: Can I use ChronoMap as a database?**  
A: ChronoMap is an in-memory store. For persistence, use `save_json()` or `save_pickle()`. For large-scale data, consider a proper database.

**Q: How do I limit history size?**  
A: Currently, you need to manually manage history. Consider periodically archiving old data or implementing custom cleanup logic.

**Q: Is ChronoMap compatible with multiprocessing?**  
A: ChronoMap is thread-safe but not process-safe. For multiprocessing, use separate instances or implement inter-process communication.

**Q: Can I use ChronoMap with Django/Flask?**  
A: Yes! ChronoMap works well as a cache layer or session store in web applications.

---

## 📄 License

## This project is licensed under the MIT License

Made with 😎 by [Devansh Singh](https://github.com/Devasnh-567)
