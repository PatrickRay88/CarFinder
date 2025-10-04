"""
Data aggregator for combining vehicle listings from multiple sources.
"""

from typing import Dict, List, Optional, Any, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from dataclasses import dataclass
import sys
from pathlib import Path

# Add app directory to path for imports
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from data_sources.base import VehicleDataSource, VehicleListing
from data_sources.cars_com import CarsDotComAPI
from data_sources.autotrader import AutoTraderAPI
from data_sources.cargurus import CarGurusAPI
from data_sources.auto_dev import AutoDevAPI

logger = logging.getLogger(__name__)

@dataclass
class SearchCriteria:
    """Search criteria for vehicle listings."""
    make: Optional[str] = None
    model: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    mileage_max: Optional[int] = None
    location: Optional[str] = None
    radius: Optional[int] = None
    limit_per_source: int = 10

class VehicleDataAggregator:
    """
    Aggregates vehicle data from multiple sources.
    Handles deduplication, ranking, and data normalization.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.sources = []
        
        # Initialize available data sources
        self._initialize_sources()
        
    def _initialize_sources(self):
        """Initialize all available data sources."""
        # Check if Auto.dev API key is available
        auto_dev_key = self.config.get('auto_dev_api_key')
        
        if auto_dev_key:
            try:
                # Use Auto.dev for live data
                auto_dev_source = AutoDevAPI(api_key=auto_dev_key)
                if auto_dev_source.test_connection():
                    self.sources.append(auto_dev_source)
                    logger.info("Initialized Auto.dev API data source")
                else:
                    logger.error("Auto.dev API connection test failed")
            except Exception as e:
                logger.error(f"Failed to initialize Auto.dev API: {e}")
        
        # Fallback to mock sources if Auto.dev is not available
        if not self.sources:
            logger.info("Auto.dev not available, using mock data sources")
            
            try:
                # Cars.com (mock implementation)
                self.sources.append(CarsDotComAPI())
                logger.info("Initialized Cars.com mock data source")
            except Exception as e:
                logger.warning(f"Failed to initialize Cars.com: {e}")
                
            try:
                # AutoTrader (mock implementation)
                api_key = self.config.get('autotrader_api_key')
                self.sources.append(AutoTraderAPI(api_key=api_key))
                logger.info("Initialized AutoTrader mock data source")
            except Exception as e:
                logger.warning(f"Failed to initialize AutoTrader: {e}")
                
            try:
                # CarGurus (mock implementation)
                api_key = self.config.get('cargurus_api_key')
                self.sources.append(CarGurusAPI(api_key=api_key))
                logger.info("Initialized CarGurus mock data source")
            except Exception as e:
                logger.warning(f"Failed to initialize CarGurus: {e}")
    
    def search_all_sources(self, criteria: SearchCriteria) -> List[VehicleListing]:
        """
        Search all available sources concurrently.
        Returns deduplicated and ranked results.
        """
        all_listings = []
        
        # Search all sources concurrently
        with ThreadPoolExecutor(max_workers=len(self.sources)) as executor:
            future_to_source = {
                executor.submit(
                    source.search_vehicles,
                    make=criteria.make,
                    model=criteria.model,
                    year_min=criteria.year_min,
                    year_max=criteria.year_max,
                    price_min=criteria.price_min,
                    price_max=criteria.price_max,
                    mileage_max=criteria.mileage_max,
                    location=criteria.location,
                    radius=criteria.radius,
                    limit=criteria.limit_per_source
                ): source for source in self.sources
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    listings = future.result(timeout=30)
                    all_listings.extend(listings)
                    logger.info(f"Retrieved {len(listings)} listings from {source.__class__.__name__}")
                except Exception as e:
                    logger.error(f"Error retrieving data from {source.__class__.__name__}: {e}")
        
        # Deduplicate based on VIN or similar vehicles
        deduplicated_listings = self._deduplicate_listings(all_listings)
        
        # Rank results
        ranked_listings = self._rank_listings(deduplicated_listings, criteria)
        
        logger.info(f"Aggregated {len(ranked_listings)} unique listings from {len(self.sources)} sources")
        return ranked_listings
    
    def _deduplicate_listings(self, listings: List[VehicleListing]) -> List[VehicleListing]:
        """Remove duplicate listings based on VIN or similarity."""
        unique_listings = []
        seen_vins = set()
        seen_similar = set()
        
        for listing in listings:
            # Check for exact VIN match
            if listing.vin and listing.vin in seen_vins:
                continue
            
            # Check for similar vehicles (same make/model/year/mileage)
            similarity_key = (
                listing.make.lower(),
                listing.model.lower(), 
                listing.year,
                listing.mileage,
                int(listing.price) if listing.price else 0
            )
            
            if similarity_key in seen_similar:
                continue
            
            unique_listings.append(listing)
            
            if listing.vin:
                seen_vins.add(listing.vin)
            seen_similar.add(similarity_key)
        
        return unique_listings
    
    def _rank_listings(self, listings: List[VehicleListing], criteria: SearchCriteria) -> List[VehicleListing]:
        """Rank listings based on relevance and quality."""
        
        def calculate_score(listing: VehicleListing) -> float:
            score = 0.0
            
            # Price preference (closer to budget midpoint is better)
            if criteria.price_min and criteria.price_max and listing.price:
                price_midpoint = (criteria.price_min + criteria.price_max) / 2
                price_deviation = abs(listing.price - price_midpoint) / price_midpoint
                score += max(0, 1 - price_deviation) * 30
            
            # Lower mileage is better
            if listing.mileage:
                # Normalize mileage score (assume 100k miles = 0 points, 0 miles = 20 points)
                mileage_score = max(0, 20 * (1 - listing.mileage / 100000))
                score += mileage_score
            
            # Newer year is better
            if listing.year:
                current_year = 2024
                age_score = max(0, 15 * (1 - (current_year - listing.year) / 10))
                score += age_score
            
            # Safety rating bonus
            if listing.safety_rating:
                score += listing.safety_rating * 5
            
            # Fuel efficiency bonus
            if listing.mpg_city and listing.mpg_highway:
                avg_mpg = (listing.mpg_city + listing.mpg_highway) / 2
                mpg_score = min(10, avg_mpg / 3)  # Up to 10 points for 30+ MPG
                score += mpg_score
            
            # Source reliability bonus (can be configured)
            source_bonus = {
                'cargurus': 5,
                'autotrader': 4,
                'cars.com': 3
            }
            score += source_bonus.get(listing.source, 0)
            
            return score
        
        # Sort by calculated score (descending)
        listings.sort(key=calculate_score, reverse=True)
        return listings
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """Get statistics about available data sources."""
        return {
            'total_sources': len(self.sources),
            'active_sources': [source.__class__.__name__ for source in self.sources],
            'source_capabilities': {
                source.__class__.__name__: {
                    'has_api_key': bool(getattr(source, 'api_key', None)),
                    'base_url': getattr(source, 'base_url', 'N/A')
                } for source in self.sources
            }
        }