#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example demonstrating SQLite Database integration with pybase.

This example shows how to configure and use native SQLite as a backend
for your pybase application with enhanced concurrency features.
"""

import os
import sys

# Add the parent directory to the path so we can import runtime modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.database_manager import DatabaseManager


def main():
    """Demonstrate SQLite Database integration."""
    print("🚀 SQLite Database Integration Example")
    print("=" * 50)

    # Reset the singleton for this example
    DatabaseManager.reset_instance()
    db_manager = DatabaseManager()

    # Example 1: Using environment variables
    print("\n1. Configuration via Environment Variables:")
    print("   Set DATABASE_URL for custom database location")
    print("   Example: export DATABASE_URL='sqlite://runtime/databases/production.db'")
    print("   Default: sqlite://runtime/databases/main.db")

    # Example 2: Direct URL configuration
    print("\n2. Direct URL Configuration:")
    print("   SQLite URLs follow these patterns:")
    print("   - sqlite://relative/path/to/database.db")
    print("   - sqlite:///absolute/path/to/database.db")

    # Example 3: Database type detection
    print("\n3. Database Type Detection:")
    test_urls = [
        "sqlite://runtime/databases/main.db",
        "sqlite:///absolute/path/to/database.db",
        "sqlite://relative.db",
        "postgres://localhost:5432/mydb"
    ]

    for url in test_urls:
        db_type = db_manager._detect_database_type(url)
        print(f"   {url} -> {db_type}")

    # Example 4: Database configuration demonstration
    print("\n4. Database Configuration (Without Full App):")
    try:
        # Demonstrate database configuration without full initialization
        db_manager._db_type = db_manager._detect_database_type("sqlite://runtime/databases/main.db")

        print(f"   ✅ Database type detected: {db_manager.database_type}")
        print(f"   ✅ Is SQLite: {db_manager.is_sqlite()}")

        # Show what configuration would be applied
        print(f"   ✅ Enhanced SQLite configuration with:")
        print(f"      - Connection pooling: 10 connections")
        print(f"      - WAL mode: Enabled for better concurrency")
        print(f"      - Journal mode: WAL")
        print(f"      - Foreign keys: ON")
        print(f"      - Cache size: 2000 (2MB)")

    except Exception as e:
        print(f"   ⚠️  Configuration failed: {e}")

    # Example 5: SQLite-specific features
    print("\n5. Enhanced SQLite Database Features:")
    print("   ✅ Native SQLite performance")
    print("   ✅ WAL mode for concurrent reads/writes")
    print("   ✅ Connection pooling for scalability")
    print("   ✅ Separate read/write connections")
    print("   ✅ Memory-mapped I/O for better performance")
    print("   ✅ Zero external dependencies")

    # Example 6: Configuration guidance
    print("\n6. Configuration Guidance:")
    print("   Production: Use DATABASE_URL with persistent storage")
    print("   Development: Use local SQLite file")
    print("   Testing: SQLite in-memory for fast test runs")
    print("   Concurrency: Enable WAL mode and connection pooling")

    print("\n📚 For more information:")
    print("   - SQLite: https://sqlite.org/")
    print("   - WAL mode: https://sqlite.org/wal.html")
    print("   - pybase documentation")


if __name__ == "__main__":
    main()