"""
Vehicle data service that integrates live data sources with the existing CarFinder system.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import json

import sys
from pathlib import Path

# Add app directory to path for absolute imports
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from models.database import DatabaseManager, Vehicle
from utils.config import load_config, get_database_url
from data_sources.aggregator import VehicleDataAggregator, SearchCriteria
from data_sources.base import VehicleListing

logger = logging.getLogger(__name__)

class VehicleDataService:
    """
    Service for managing vehicle data from multiple sources.
    Integrates live data with local database and caching.
    """
    
    def __init__(self):
        self.config = load_config()
        database_url = get_database_url(self.config)
        self.db_manager = DatabaseManager(database_url)
        self.aggregator = VehicleDataAggregator(self.config)
        self.cache_duration = timedelta(hours=2)  # Cache live data for 2 hours
        
    def search_vehicles_hybrid(self, preferences: Dict[str, Any], use_live_data: bool = True) -> List[Dict[str, Any]]:
        """
        Hybrid search combining local database and live data sources.
        
        Args:
            preferences: Search preferences from user
            use_live_data: Whether to include live data sources
            
        Returns:
            Combined results from local DB and/or live sources
        """
        results = []
        
        if use_live_data:
            # When live data is ON, use ONLY live sources for pure live experience
            try:
                live_results = self._search_live_sources(preferences)
                results.extend(live_results)
                logger.info(f"Live mode: Found {len(live_results)} vehicles from live sources only")
                
                # Optionally cache live results to local database
                if live_results:
                    self._cache_live_results(live_results)
                    
                # DON'T mix local results when in pure live mode
                # local_results = self._search_local_database(preferences)
                # results.extend(local_results)
                # logger.info(f"Found {len(local_results)} additional vehicles in local database")
                    
            except Exception as e:
                logger.error(f"Error searching live sources: {e}")
                # Fallback to local database if live sources fail
                local_results = self._search_local_database(preferences)
                results.extend(local_results)
                logger.info(f"Fallback: Found {len(local_results)} vehicles in local database")
        else:
            # When live data is OFF, use only local database
            local_results = self._search_local_database(preferences)
            results.extend(local_results)
            logger.info(f"Local only: Found {len(local_results)} vehicles in local database")
        
        # Remove duplicates and sort by relevance
        unique_results = self._deduplicate_results(results)
        sorted_results = self._sort_by_relevance(unique_results, preferences)
        
        return sorted_results[:preferences.get('limit', 20)]
    
    def _search_local_database(self, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search the local SQLite database."""
        # Convert vehicle_type to make filter for trucks
        make_filter = preferences.get('make')
        vehicle_type = preferences.get('vehicle_type')
        
        # If looking for trucks, filter by truck makes/models
        if vehicle_type == 'truck' and not make_filter:
            truck_makes = ['Ford', 'Chevrolet', 'Toyota', 'Ram', 'GMC', 'Nissan']
            # For now, search each truck make (this could be optimized)
            all_vehicles = []
            for truck_make in truck_makes[:3]:  # Limit to top 3 makes
                vehicles = self.db_manager.search_vehicles(
                    make=truck_make,
                    model=preferences.get('model'),
                    min_year=preferences.get('year_min'),
                    max_year=preferences.get('year_max'),
                    min_price=preferences.get('price_min'),
                    max_price=preferences.get('budget_max'),
                    max_mileage=preferences.get('mileage_max'),
                    fuel_type=preferences.get('fuel_type'),
                    limit=20
                )
                all_vehicles.extend(vehicles)
            return [self._vehicle_to_dict(vehicle) for vehicle in all_vehicles]
        else:
            vehicles = self.db_manager.search_vehicles(
                make=make_filter,
                model=preferences.get('model'),
                min_year=preferences.get('year_min'),
                max_year=preferences.get('year_max'),
                min_price=preferences.get('price_min'),
                max_price=preferences.get('budget_max'),
                max_mileage=preferences.get('mileage_max'),
                fuel_type=preferences.get('fuel_type'),
                limit=50
            )
        
        return [self._vehicle_to_dict(vehicle) for vehicle in vehicles]
    
    def _search_live_sources(self, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search live data sources through the aggregator."""
        make_filter = preferences.get('make')
        vehicle_type = preferences.get('vehicle_type')
        
        # If searching for trucks, use truck-specific makes
        if vehicle_type == 'truck' and not make_filter:
            truck_results = []
            truck_makes = ['Ford', 'Chevrolet', 'Toyota', 'Ram', 'GMC']
            
            for truck_make in truck_makes:
                criteria = SearchCriteria(
                    make=truck_make,
                    model=preferences.get('model'), 
                    year_min=preferences.get('year_min'),
                    year_max=preferences.get('year_max'),
                    price_min=preferences.get('price_min'),
                    price_max=preferences.get('budget_max'),
                    mileage_max=preferences.get('mileage_max'),
                    location=preferences.get('location'),
                    radius=preferences.get('radius', 50),
                    limit_per_source=3
                )
                listings = self.aggregator.search_all_sources(criteria)
                truck_results.extend(listings)
            
            # Filter to only include actual truck models and specific class if requested
            filtered_trucks = self._filter_truck_models(truck_results, preferences)
            return [self._listing_to_dict(listing) for listing in filtered_trucks]
        else:
            criteria = SearchCriteria(
                make=make_filter,
                model=preferences.get('model'), 
                year_min=preferences.get('year_min'),
                year_max=preferences.get('year_max'),
                price_min=preferences.get('price_min'),
                price_max=preferences.get('budget_max'),
                mileage_max=preferences.get('mileage_max'),
                location=preferences.get('location'),
                radius=preferences.get('radius', 50),
                limit_per_source=10
            )
        
        live_listings = self.aggregator.search_all_sources(criteria)
        return [self._listing_to_dict(listing) for listing in live_listings]
    
    def _filter_truck_models(self, listings, preferences=None):
        """Filter listings to only include actual truck models, optionally by truck class."""
        truck_models = ['f-150', 'f150', 'silverado', 'sierra', 'tacoma', 'tundra', 'ram', 'frontier', 'ranger', 'colorado', 'canyon', 'ridgeline', 'truck', '1500', '2500', '3500']
        
        # Get truck class preference if specified (1500, 2500, 3500)
        truck_class = preferences.get('truck_class') if preferences else None
        
        filtered = []
        for listing in listings:
            model = listing.model.lower() if listing.model else ''
            
            # Check if the model contains truck-specific keywords
            is_truck = any(truck_model in model for truck_model in truck_models)
            
            if is_truck:
                # If truck class is specified, filter by that class
                if truck_class:
                    if truck_class in model:
                        filtered.append(listing)
                        logger.info(f"Kept {truck_class} truck: {listing.make} {listing.model}")
                    else:
                        logger.info(f"Filtered out wrong truck class: {listing.make} {listing.model} (wanted {truck_class})")
                else:
                    filtered.append(listing)
                    logger.info(f"Kept truck: {listing.make} {listing.model}")
            else:
                logger.info(f"Filtered out non-truck: {listing.make} {listing.model}")
        
        return filtered
    
    def _cache_live_results(self, live_results: List[Dict[str, Any]]) -> None:
        """Cache live results to local database for future searches."""
        try:
            for result in live_results:
                # Check if vehicle already exists by VIN or external ID
                existing = None
                if result.get('vin'):
                    existing = self.db_manager.get_vehicle_by_vin(result['vin'])
                
                if not existing:
                    # Create new vehicle record
                    vehicle_data = {
                        'make': result['make'],
                        'model': result['model'],
                        'year': result['year'],
                        'price': result['price'],
                        'mileage': result['mileage'],
                        'fuel_type': result['fuel_type'],
                        'transmission': result['transmission'],
                        'location': result['location'],
                        'safety_rating': result['safety_rating'],
                        'mpg_city': result['mpg_city'],
                        'mpg_highway': result['mpg_highway'],
                        'vin': result['vin'],
                        'description': result['description'],
                        'features': json.dumps(result.get('features', []))  # Convert to JSON string
                    }
                    
                    vehicle = Vehicle(**vehicle_data)
                    self.db_manager.add_vehicle(vehicle)
                    
            logger.info(f"Cached {len(live_results)} live results to database")
            
        except Exception as e:
            logger.error(f"Error caching live results: {e}")
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate vehicles from combined results."""
        unique_results = []
        seen_vins = set()
        seen_similar = set()
        
        for result in results:
            # Check for VIN duplicates
            vin = result.get('vin')
            if vin and vin in seen_vins:
                continue
                
            # Check for similar vehicles
            similarity_key = (
                result.get('make', '').lower(),
                result.get('model', '').lower(),
                result.get('year'),
                result.get('mileage'),
                int(result.get('price', 0))
            )
            
            if similarity_key in seen_similar:
                continue
                
            unique_results.append(result)
            
            if vin:
                seen_vins.add(vin)
            seen_similar.add(similarity_key)
        
        return unique_results
    
    def _sort_by_relevance(self, results: List[Dict[str, Any]], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sort results by relevance to user preferences."""
        
        def relevance_score(vehicle: Dict[str, Any]) -> float:
            score = 0.0
            
            # Prefer vehicles from live sources (more up-to-date)
            if vehicle.get('source') in ['cars.com', 'autotrader', 'cargurus']:
                score += 10
            
            # Price preference
            budget_max = preferences.get('budget_max')
            if budget_max and vehicle.get('price'):
                if vehicle['price'] <= budget_max:
                    price_ratio = vehicle['price'] / budget_max
                    score += (1 - price_ratio) * 20  # Cheaper is better within budget
            
            # Mileage preference (lower is better)
            mileage = vehicle.get('mileage', 0)
            if mileage:
                mileage_score = max(0, 15 * (1 - mileage / 150000))  # Normalize to 150k miles
                score += mileage_score
            
            # Year preference (newer is better)
            year = vehicle.get('year')
            if year:
                current_year = datetime.now().year
                age_score = max(0, 10 * (1 - (current_year - year) / 15))  # Normalize to 15 years
                score += age_score
            
            # Fuel type preference
            preferred_fuel = preferences.get('fuel_type')
            if preferred_fuel and vehicle.get('fuel_type') == preferred_fuel:
                score += 15
            
            # Safety rating
            safety_rating = vehicle.get('safety_rating')
            if safety_rating:
                score += safety_rating * 3
            
            return score
        
        return sorted(results, key=relevance_score, reverse=True)
    
    def _vehicle_to_dict(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Convert Vehicle model to dictionary."""
        return vehicle.to_dict()
    
    def _listing_to_dict(self, listing: VehicleListing) -> Dict[str, Any]:
        """Convert VehicleListing to dictionary."""
        return listing.to_dict()
    
    def get_data_source_status(self) -> Dict[str, Any]:
        """Get status information about data sources."""
        return {
            'local_database': {
                'vehicle_count': self.db_manager.get_total_vehicles(),
                'status': 'active'
            },
            'live_sources': self.aggregator.get_source_statistics()
        }
    
    def refresh_live_data(self, preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manually refresh live data for current search criteria."""
        if not preferences:
            preferences = {'budget_max': 50000, 'limit': 50}  # Default broad search
            
        try:
            live_results = self._search_live_sources(preferences)
            if live_results:
                self._cache_live_results(live_results)
                
            return {
                'success': True,
                'new_listings': len(live_results),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error refreshing live data: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }