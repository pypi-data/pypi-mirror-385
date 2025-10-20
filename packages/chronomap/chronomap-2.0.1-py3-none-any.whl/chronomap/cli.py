import argparse
import json
import time
from pathlib import Path
from .chronomap import ChronoMap
"""
ChronoMap CLI - Command-line interface for experimenting with ChronoMap.

Usage:
    python -m chronomap                    # Interactive mode
    python -m chronomap --demo             # Run demo
    python -m chronomap --file data.json   # Load from file
"""
def interactive_mode():
    """Run interactive ChronoMap shell."""
    print("=" * 60)
    print("ChronoMap Interactive Shell")
    print("=" * 60)
    print("\nCommands:")
    print("  put <key> <value>    - Store a value")
    print("  get <key>            - Retrieve a value")
    print("  delete <key>         - Delete a key")
    print("  history <key>        - Show key history")
    print("  latest               - Show all latest values")
    print("  snapshot             - Take a snapshot")
    print("  rollback             - Rollback to last snapshot")
    print("  clear                - Clear all data")
    print("  save <file>          - Save to JSON file")
    print("  load <file>          - Load from JSON file")
    print("  help                 - Show this help")
    print("  exit                 - Exit shell")
    print()
    
    cm = ChronoMap(debug=False)
    snapshot_stack = []
    
    while True:
        try:
            cmd = input("chronomap> ").strip()
            if not cmd:
                continue
            
            parts = cmd.split(maxsplit=2)
            command = parts[0].lower()
            
            if command == 'exit':
                print("Goodbye!")
                break
            
            elif command == 'help':
                print("\nCommands:")
                print("  put <key> <value>    - Store a value")
                print("  get <key>            - Retrieve a value")
                print("  delete <key>         - Delete a key")
                print("  history <key>        - Show key history")
                print("  latest               - Show all latest values")
                print("  snapshot             - Take a snapshot")
                print("  rollback             - Rollback to last snapshot")
                print("  clear                - Clear all data")
                print("  save <file>          - Save to JSON file")
                print("  load <file>          - Load from JSON file")
                print("  exit                 - Exit shell\n")
            
            elif command == 'put':
                if len(parts) < 3:
                    print("Usage: put <key> <value>")
                    continue
                key = parts[1]
                value = parts[2]
                # Try to parse as JSON for complex values
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass  # Keep as string
                cm[key] = value
                print(f"✓ Stored: {key} = {value}")
            
            elif command == 'get':
                if len(parts) < 2:
                    print("Usage: get <key>")
                    continue
                key = parts[1]
                value = cm.get(key)
                if value is None:
                    print(f"✗ Key '{key}' not found")
                else:
                    print(f"→ {key} = {value}")
            
            elif command == 'delete':
                if len(parts) < 2:
                    print("Usage: delete <key>")
                    continue
                key = parts[1]
                if cm.delete(key):
                    print(f"✓ Deleted: {key}")
                else:
                    print(f"✗ Key '{key}' not found")
            
            elif command == 'history':
                if len(parts) < 2:
                    print("Usage: history <key>")
                    continue
                key = parts[1]
                history = cm.history(key)
                if not history:
                    print(f"✗ No history for key '{key}'")
                else:
                    print(f"\nHistory for '{key}':")
                    for ts, val in history:
                        print(f"  {ts:.2f}: {val}")
            
            elif command == 'latest':
                latest = cm.latest()
                if not latest:
                    print("✗ Map is empty")
                else:
                    print("\nLatest values:")
                    for key, value in sorted(latest.items()):
                        print(f"  {key}: {value}")
            
            elif command == 'snapshot':
                snap = cm.snapshot()
                snapshot_stack.append(snap)
                print(f"✓ Snapshot taken (total: {len(snapshot_stack)})")
            
            elif command == 'rollback':
                if not snapshot_stack:
                    print("✗ No snapshots available")
                else:
                    snap = snapshot_stack.pop()
                    cm.rollback(snap)
                    print(f"✓ Rolled back (remaining: {len(snapshot_stack)})")
            
            elif command == 'clear':
                cm.clear()
                print("✓ Cleared all data")
            
            elif command == 'save':
                if len(parts) < 2:
                    print("Usage: save <file>")
                    continue
                filepath = parts[1]
                cm.save_json(filepath)
                print(f"✓ Saved to {filepath}")
            
            elif command == 'load':
                if len(parts) < 2:
                    print("Usage: load <file>")
                    continue
                filepath = parts[1]
                cm = ChronoMap.load_json(filepath)
                snapshot_stack.clear()
                print(f"✓ Loaded from {filepath}")
            
            else:
                print(f"✗ Unknown command: {command}")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"✗ Error: {e}")


def run_demo():
    """Run a demonstration of ChronoMap features."""
    print("=" * 60)
    print("ChronoMap Feature Demonstration")
    print("=" * 60)
    
    cm = ChronoMap()
    
    # Basic operations
    print("\n1. Basic Operations")
    print("-" * 40)
    cm['name'] = 'Alice'
    cm['age'] = 30
    cm['city'] = 'New York'
    print(f"Stored data: {cm.latest()}")
    print(f"Get name: {cm['name']}")
    print(f"Map has {len(cm)} keys")
    
    # Time-versioned storage
    print("\n2. Time-Versioned Storage")
    print("-" * 40)
    cm.put('temperature', 20, timestamp=100)
    cm.put('temperature', 22, timestamp=200)
    cm.put('temperature', 24, timestamp=300)
    print(f"Temp at t=150: {cm.get('temperature', timestamp=150)}")
    print(f"Temp at t=250: {cm.get('temperature', timestamp=250)}")
    print(f"History: {cm.history('temperature')}")
    
    # Batch operations
    print("\n3. Batch Operations")
    print("-" * 40)
    cm.put_many({'user1': 'active', 'user2': 'active', 'user3': 'inactive'})
    print(f"Added users: {[k for k in cm.keys() if k.startswith('user')]}")
    deleted = cm.delete_many(['user2', 'user3'])
    print(f"Deleted {deleted} users")
    
    # Snapshots and rollback
    print("\n4. Snapshots and Rollback")
    print("-" * 40)
    snap = cm.snapshot()
    print(f"Snapshot taken with {len(snap)} keys")
    cm['new_key'] = 'new_value'
    cm['age'] = 31
    print(f"After changes: age={cm['age']}, new_key={cm.get('new_key')}")
    cm.rollback(snap)
    print(f"After rollback: age={cm['age']}, new_key={cm.get('new_key')}")
    
    # Advanced queries
    print("\n5. Advanced Queries")
    print("-" * 40)
    cm.clear()
    cm.put('sensor', 10, timestamp=100)
    cm.put('sensor', 15, timestamp=200)
    cm.put('sensor', 20, timestamp=300)
    cm.put('sensor', 25, timestamp=400)
    range_data = cm.get_range('sensor', start_ts=150, end_ts=350)
    print(f"Sensor readings [150-350]: {range_data}")
    
    # TTL / Expiry
    print("\n6. TTL / Expiry (demo)")
    print("-" * 40)
    print("Would store session with TTL=3600 seconds")
    print("Session would auto-expire after 1 hour")
    
    # Merge
    print("\n7. Merge")
    print("-" * 40)
    cm1 = ChronoMap()
    cm2 = ChronoMap()
    cm1.put('shared', 'value1', timestamp=100)
    cm2.put('shared', 'value2', timestamp=200)
    cm2.put('unique', 'data')
    cm1.merge(cm2)
    print(f"After merge: {cm1.history('shared')}")
    print(f"Merged keys: {list(cm1.keys())}")
    
    # Persistence
    print("\n8. Persistence")
    print("-" * 40)
    print("ChronoMap supports:")
    print("  - JSON serialization: save_json() / load_json()")
    print("  - Pickle serialization: save_pickle() / load_pickle()")
    print("  - Dict conversion: to_dict() / from_dict()")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


def load_and_display(filepath: str):
    """Load and display ChronoMap from file."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"Error: File '{filepath}' not found")
        return
    
    try:
        if path.suffix == '.json':
            cm = ChronoMap.load_json(filepath)
        elif path.suffix == '.pkl':
            cm = ChronoMap.load_pickle(filepath)
        else:
            print(f"Error: Unsupported file type '{path.suffix}'")
            return
        
        print(f"Loaded ChronoMap from {filepath}")
        print(f"Keys: {len(cm)}")
        print(f"\nLatest values:")
        for key, value in sorted(cm.latest().items()):
            print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"Error loading file: {e}")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="ChronoMap - Time-versioned key-value store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m chronomap              Start interactive shell
  python -m chronomap --demo       Run feature demonstration
  python -m chronomap --file data.json   Load and display file
        """
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run feature demonstration'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Load and display ChronoMap from file'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='Show version information'
    )
    
    args = parser.parse_args()
    
    if args.version:
        from chronomap import __version__
        print(f"ChronoMap version {__version__}")
        return
    
    if args.demo:
        run_demo()
    elif args.file:
        load_and_display(args.file)
    else:
        interactive_mode()


if __name__ == '__main__':
    main()