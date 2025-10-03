"""
Test script for live data integration
"""

import sys
import os
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

try:
    from utils.config import load_config
    print("✅ Config module loaded")
    
    from models.database import DatabaseManager
    print("✅ Database manager loaded")
    
    from data_sources.base import VehicleDataSource, VehicleListing
    print("✅ Base data source classes loaded")
    
    from data_sources.cars_com import CarsDotComAPI
    from data_sources.autotrader import AutoTraderAPI
    from data_sources.cargurus import CarGurusAPI
    print("✅ All data source APIs loaded")
    
    from data_sources.aggregator import VehicleDataAggregator
    print("✅ Data aggregator loaded")
    
    print("\n🎉 All live data components loaded successfully!")
    print("📦 Ready for real-time vehicle data integration")
    
    # Test basic functionality
    config = load_config()
    db = DatabaseManager(f"sqlite:///{config['database_path']}")
    
    # Initialize database if needed
    try:
        db.init_database()
        total_vehicles = db.get_total_vehicles()
        print(f"📊 Local database contains {total_vehicles} vehicles")
    except Exception as e:
        print(f"⚠️ Database not initialized yet: {e}")
        print("💡 Run 'python scripts/setup_database.py' to initialize")
    
    # Test aggregator
    aggregator = VehicleDataAggregator(config)
    stats = aggregator.get_source_statistics()
    print(f"🌐 {stats['total_sources']} live data sources configured")
    
    for source_name in stats['active_sources']:
        print(f"  • {source_name}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")