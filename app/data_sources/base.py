"""
Base class and utilities for vehicle data source integrations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class VehicleListing:
    """Standardized vehicle listing data structure."""
    source: str
    external_id: str
    make: str
    model: str
    year: int
    price: Optional[float]
    mileage: Optional[int]
    fuel_type: Optional[str]
    transmission: Optional[str]
    location: Optional[str]
    safety_rating: Optional[int]
    mpg_city: Optional[int]
    mpg_highway: Optional[int]
    vin: Optional[str]
    description: Optional[str]
    features: List[str]
    images: List[str]
    dealer_name: Optional[str]
    dealer_phone: Optional[str]
    listing_url: Optional[str]
    listing_date: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'source': self.source,
            'external_id': self.external_id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'price': self.price,
            'mileage': self.mileage,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'location': self.location,
            'safety_rating': self.safety_rating,
            'mpg_city': self.mpg_city,
            'mpg_highway': self.mpg_highway,
            'vin': self.vin,
            'description': self.description,
            'features': self.features,
            'images': self.images,
            'dealer_name': self.dealer_name,
            'dealer_phone': self.dealer_phone,
            'listing_url': self.listing_url,
            'listing_date': self.listing_date
        }

class VehicleDataSource(ABC):
    """Abstract base class for vehicle data sources."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        
    @abstractmethod
    def search_vehicles(self, 
                       make: Optional[str] = None,
                       model: Optional[str] = None,
                       year_min: Optional[int] = None,
                       year_max: Optional[int] = None,
                       price_min: Optional[float] = None,
                       price_max: Optional[float] = None,
                       mileage_max: Optional[int] = None,
                       location: Optional[str] = None,
                       radius: Optional[int] = None,
                       limit: int = 20) -> List[VehicleListing]:
        """Search for vehicles matching criteria."""
        pass
    
    @abstractmethod
    def get_vehicle_details(self, external_id: str) -> Optional[VehicleListing]:
        """Get detailed information for a specific vehicle."""
        pass
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """Make HTTP request with error handling."""
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None