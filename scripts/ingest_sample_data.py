#!/usr/bin/env python3
"""Ingest sample vehicle data into CarFinder database."""

import sys
import csv
import json
from pathlib import Path

# Add the app directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.utils.config import load_config, get_database_url
from app.models.database import get_database_manager

def main():
    """Ingest sample vehicle data."""
    print("🚗 CarFinder Data Ingestion")
    print("=" * 30)
    
    # Load configuration
    config = load_config()
    database_url = get_database_url(config)
    db_manager = get_database_manager(database_url)
    
    # Path to sample data
    sample_data_path = project_root / "data" / "sample_listings.csv"
    
    if not sample_data_path.exists():
        print(f"❌ Sample data file not found: {sample_data_path}")
        sys.exit(1)
    
    print(f"📁 Loading data from: {sample_data_path}")
    
    try:
        vehicles_added = 0
        
        with open(sample_data_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Parse features from JSON string
                features_str = row.get('features', '[]')
                try:
                    features = json.loads(features_str.replace("'", '"'))
                except (json.JSONDecodeError, AttributeError):
                    features = []
                
                # Prepare vehicle data
                vehicle_data = {
                    'make': row['make'],
                    'model': row['model'],
                    'year': int(row['year']) if row['year'] else None,
                    'price': float(row['price']) if row['price'] else None,
                    'mileage': int(row['mileage']) if row['mileage'] else None,
                    'fuel_type': row['fuel_type'] if row['fuel_type'] else None,
                    'transmission': row['transmission'] if row['transmission'] else None,
                    'location': row['location'] if row['location'] else None,
                    'safety_rating': float(row['safety_rating']) if row['safety_rating'] else None,
                    'mpg_city': int(row['mpg_city']) if row['mpg_city'] else None,
                    'mpg_highway': int(row['mpg_highway']) if row['mpg_highway'] else None,
                    'vin': row['vin'] if row['vin'] else None,
                    'description': row['description'] if row['description'] else None,
                    'features': json.dumps(features)
                }
                
                # Check if vehicle already exists by VIN
                if vehicle_data['vin']:
                    existing = db_manager.get_vehicle_by_vin(vehicle_data['vin'])
                    if existing:
                        print(f"⏭️  Skipping existing vehicle: {vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}")
                        continue
                
                # Add vehicle to database
                vehicle = db_manager.add_vehicle(vehicle_data)
                vehicles_added += 1
                
                print(f"✅ Added: {vehicle.year} {vehicle.make} {vehicle.model} (ID: {vehicle.id})")
        
        print(f"\n🎉 Successfully added {vehicles_added} vehicles to the database!")
        
        # Show updated stats
        stats = db_manager.get_vehicle_stats()
        print(f"📈 Total vehicles in database: {stats['total_vehicles']}")
        print(f"🏭 Unique makes: {stats['unique_makes']}")
        print(f"💰 Price range: ${stats['price_range'][0]:,.0f} - ${stats['price_range'][1]:,.0f}")
        
        print("\n💡 Next steps:")
        print("   1. Run 'python scripts/update_embeddings.py' to create search index")
        print("   2. Start the app with 'streamlit run app/main.py'")
        
    except Exception as e:
        print(f"❌ Error ingesting data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()