#!/usr/bin/env python3
"""
Uninstall script for coaxial-wakesleepmanager.
This script is called when the package is uninstalled to optionally preserve user settings.
"""

import os
import sys
import json
import shutil
from pathlib import Path

def main():
    """Handle package uninstallation with option to preserve settings."""
    config_dir = Path.home() / ".config" / "wakesleepmanager"
    devices_file = config_dir / "devices.json"

    print("\n" + "="*60)
    print("🔧 Coaxial WakeSleepManager - Uninstall")
    print("="*60)

    # Check if config exists
    if not config_dir.exists():
        print("✅ No configuration found. Safe to uninstall.")
        return

    # Check if devices.json exists and has content
    has_devices = False
    if devices_file.exists():
        try:
            with open(devices_file, 'r') as f:
                data = json.load(f)
                if data and len(data) > 0:
                    has_devices = True
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    if not has_devices:
        print("✅ No device configurations found. Safe to uninstall.")
        return

    print(f"\n📁 Configuration found at: {config_dir}")
    print(f"📊 Devices configured: {len(data) if has_devices else 0}")

    # Show what will be deleted
    print("\n🗑️  The following will be removed:")
    print(f"   • Configuration directory: {config_dir}")
    print(f"   • Device settings and SSH credentials")
    print(f"   • All saved device configurations")

    # Ask user what to do
    print("\n❓ What would you like to do?")
    print("   1. Keep settings (recommended if you plan to reinstall)")
    print("   2. Delete all settings")
    print("   3. Cancel uninstall")

    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice == "1":
                print("✅ Settings preserved. You can reinstall later and your devices will still be configured.")
                print(f"   Settings kept at: {config_dir}")
                break
            elif choice == "2":
                if input("⚠️  Are you sure you want to delete ALL settings? (yes/no): ").lower() == "yes":
                    shutil.rmtree(config_dir)
                    print("🗑️  All settings deleted.")
                else:
                    print("❌ Uninstall cancelled.")
                    sys.exit(1)
                break
            elif choice == "3":
                print("❌ Uninstall cancelled.")
                sys.exit(1)
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n❌ Uninstall cancelled.")
            sys.exit(1)

    print("\n✅ Uninstall complete!")

if __name__ == "__main__":
    main()
