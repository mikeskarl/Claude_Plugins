#!/usr/bin/env python3
"""
Configuration management for quiz-maker plugin.
Handles storage path setup and validation.
"""

import json
import sys
from pathlib import Path


CONFIG_FILE = Path.home() / ".claude" / "plugins" / "marketplaces" / "custom-plugins" / "quiz-maker-plugin" / "skills" / "quiz-maker" / "user_config.json"


def get_default_config():
    """Return default configuration."""
    return {
        "storage_root": str(Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "Family" / "StudyGuides"),
        "configured": False
    }


def load_config():
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return get_default_config()

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Ensure all required keys exist
            defaults = get_default_config()
            for key in defaults:
                if key not in config:
                    config[key] = defaults[key]
            return config
    except Exception as e:
        print(f"ERROR: Failed to load config: {e}", file=sys.stderr)
        return get_default_config()


def save_config(config):
    """Save configuration to file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save config: {e}", file=sys.stderr)
        return False


def configure_interactive():
    """Interactive configuration setup."""
    print("\n=== Quiz Maker Configuration ===\n")

    config = get_default_config()

    print("Where should quiz files be saved?")
    print(f"Default: {config['storage_root']}")
    storage_input = input("Storage path (press Enter for default): ").strip()

    if storage_input:
        storage_path = Path(storage_input).expanduser()
    else:
        storage_path = Path(config['storage_root'])

    # Validate path
    if not storage_path.exists():
        print(f"\nDirectory does not exist: {storage_path}")
        create = input("Create it now? (y/n): ").strip().lower()
        if create == 'y':
            try:
                storage_path.mkdir(parents=True, exist_ok=True)
                print(f"Created: {storage_path}")
            except Exception as e:
                print(f"ERROR: Could not create directory: {e}", file=sys.stderr)
                return False
        else:
            print("Configuration cancelled.")
            return False

    config['storage_root'] = str(storage_path)
    config['configured'] = True

    if save_config(config):
        print("\n✓ Configuration saved successfully!")
        print(f"  Storage root: {config['storage_root']}")
        return True
    else:
        return False


def ensure_configured():
    """Ensure configuration exists, prompt if not."""
    config = load_config()

    if not config.get('configured', False):
        print("First-time setup required.")
        return configure_interactive()

    return True


def get_storage_root():
    """Get configured storage root path."""
    config = load_config()
    return Path(config['storage_root'])


def main():
    """Main entry point for config management."""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--reconfigure':
            return 0 if configure_interactive() else 1
        elif sys.argv[1] == '--check':
            config = load_config()
            print("\n=== Current Configuration ===")
            print(f"Storage root: {config['storage_root']}")
            print(f"Configured: {config.get('configured', False)}")

            storage_path = Path(config['storage_root'])
            print(f"Path exists: {storage_path.exists()}")
            return 0
        else:
            print("Usage: config.py [--reconfigure|--check]", file=sys.stderr)
            return 1

    # No args - ensure configured
    return 0 if ensure_configured() else 1


if __name__ == "__main__":
    sys.exit(main())
