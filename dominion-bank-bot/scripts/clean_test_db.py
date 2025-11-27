"""
Clean test database before running tests.
Removes the database file to ensure a fresh start.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_PATH = "data/phantom.db"


def clean_database():
    """Remove the database file if it exists."""
    if os.path.exists(DATABASE_PATH):
        try:
            os.remove(DATABASE_PATH)
            print(f"✅ Database cleaned: {DATABASE_PATH}")
        except Exception as e:
            print(f"❌ Error removing database: {e}")
            return False
    else:
        print(f"ℹ️ Database does not exist: {DATABASE_PATH}")
    return True


def main():
    """Main entry point."""
    print("🧹 Cleaning test environment...")
    success = clean_database()
    if success:
        print("✅ Test environment is clean!")
    else:
        print("❌ Failed to clean test environment")
        sys.exit(1)


if __name__ == "__main__":
    main()
