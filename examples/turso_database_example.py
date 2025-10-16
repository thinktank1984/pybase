#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example demonstrating Turso Database integration with pybase.

This example shows how to configure and use Turso Database as a backend
for your pybase application.
"""

import os
import sys

# Add the parent directory to the path so we can import runtime modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.database_manager import DatabaseManager


def main():
    """Demonstrate Turso Database integration."""
    print("🚀 Turso Database Integration Example")
    print("=" * 50)

    # Reset the singleton for this example
    DatabaseManager.reset_instance()
    db_manager = DatabaseManager()

    # Example 1: Using environment variables
    print("\n1. Configuration via Environment Variables:")
    print("   Set TURSO_DATABASE_URL and TURSO_AUTH_TOKEN")
    print("   Example: export TURSO_DATABASE_URL='libsql://my-app.turso.io'")
    print("   Example: export TURSO_AUTH_TOKEN='your-auth-token-here'")

    # Example 2: Direct URL configuration
    print("\n2. Direct URL Configuration:")
    print("   Turso URLs follow these patterns:")
    print("   - libsql://your-database-name.turso.io")
    print("   - libsql://your-database-name.turso.io#auth-token")

    # Example 3: Database type detection
    print("\n3. Database Type Detection:")
    test_urls = [
        "libsql://my-app.turso.io",
        "https://production-db.turso.io",
        "sqlite://local.db",
        "postgres://localhost:5432/mydb"
    ]

    for url in test_urls:
        db_type = db_manager._detect_database_type(url)
        print(f"   {url} -> {db_type}")

    # Example 4: Database configuration demonstration
    print("\n4. Database Configuration (Without Full App):")
    try:
        # Demonstrate database configuration without full initialization
        db_manager._db_type = db_manager._detect_database_type("sqlite://runtime/databases/bloggy.turso.db")

        print(f"   ✅ Database type detected: {db_manager.database_type}")
        print(f"   ✅ Is Turso: {db_manager.is_turso()}")

        # Show what configuration would be applied
        print(f"   ✅ Would configure SQLite with:")
        print(f"      - Pool size: 0 (no pooling)")
        print(f"      - Journal mode: DELETE")
        print(f"      - Foreign keys: ON")

    except Exception as e:
        print(f"   ⚠️  Configuration failed: {e}")

    # Example 5: Turso-specific features
    print("\n5. Turso Database Features:")
    print("   ✅ SQLite-compatible API")
    print("   ✅ Edge-native deployment")
    print("   ✅ Automatic replication")
    print("   ✅ Built-in connection pooling")
    print("   ✅ Retry logic with exponential backoff")
    print("   ✅ Graceful fallback to SQLite")

    # Example 6: Configuration guidance
    print("\n6. Configuration Guidance:")
    print("   Production: Use TURSO_DATABASE_URL environment variable")
    print("   Development: Use local SQLite for fast iteration")
    print("   Testing: SQLite in-memory for fast test runs")
    print("   Fallback: Automatic SQLite fallback if Turso is unavailable")

    print("\n📚 For more information:")
    print("   - Turso: https://turso.tech/")
    print("   - libsql-client: pip install libsql-client")
    print("   - pybase documentation")


if __name__ == "__main__":
    main()