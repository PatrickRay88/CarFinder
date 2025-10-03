#!/usr/bin/env python3
"""Database setup script for CarFinder."""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.utils.config import load_config, get_database_url
from app.models.database import init_database, get_database_manager

def main():
    """Initialize the CarFinder database."""
    print("🚗 CarFinder Database Setup")
    print("=" * 30)
    
    # Load configuration
    config = load_config()
    database_url = get_database_url(config)
    
    print(f"Database URL: {database_url}")
    
    try:
        # Initialize database
        print("\n📊 Creating database tables...")
        init_database(database_url)
        
        # Test database connection
        print("\n🔍 Testing database connection...")
        db_manager = get_database_manager(database_url)
        stats = db_manager.get_vehicle_stats()
        
        print(f"✅ Database initialized successfully!")
        print(f"📈 Current stats: {stats['total_vehicles']} vehicles in database")
        
        if stats['total_vehicles'] == 0:
            print("\n💡 Tip: Run 'python scripts/ingest_sample_data.py' to add sample vehicle data.")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)
    
    print("\n🎉 Database setup complete!")

if __name__ == "__main__":
    main()