"""
Auto.dev API integration for real-time vehicle listings.
"""

from typing import Dict, List, Optional, Any
import requests
import logging
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from data_sources.base import VehicleDataSource, VehicleListing

logger = logging.getLogger(__name__)

class AutoDevAPI(VehicleDataSource):
    """
    Auto.dev API integration for real vehicle data.
    """
    
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
        self.base_url = "https://api.auto.dev"
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'CarFinder/1.0'
        })
        
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
        """Search vehicles on Auto.dev API."""
        
        try:
            # Build query parameters for Auto.dev API
            params = {
                'limit': min(limit, 100),  # API supports up to 100 results per page
            }
            
            # Add filters based on search criteria using Auto.dev parameter format
            if make:
                params['vehicle.make'] = make
            if model:
                params['vehicle.model'] = model
            if year_min and year_max:
                params['vehicle.year'] = f"{year_min}-{year_max}"
            elif year_min:
                params['vehicle.year'] = str(year_min)
            if price_min and price_max:
                params['retailListing.price'] = f"{int(price_min)}-{int(price_max)}"
            elif price_max:
                params['retailListing.price'] = f"1-{int(price_max)}"
            if mileage_max:
                params['retailListing.miles'] = f"0-{int(mileage_max)}"  # Fixed: mileage is in retailListing.miles
            if location:
                params['zip'] = location
            if radius:
                params['distance'] = radius
            
            # Make API request
            response = self._make_request('listings', params)
            
            if response and 'data' in response:
                vehicles = response['data']
                logger.info(f"Auto.dev API returned {len(vehicles)} vehicles")
                
                # Convert API response to VehicleListing objects
                listings = []
                for vehicle_data in vehicles:
                    try:
                        listing = self._parse_vehicle_data(vehicle_data)
                        if listing:
                            # Post-process filtering (backup in case API doesn't filter properly)
                            if mileage_max and listing.mileage and listing.mileage > mileage_max:
                                logger.info(f"Filtered out {listing.make} {listing.model} - {listing.mileage:,} miles exceeds {mileage_max:,} mile limit")
                                continue
                            listings.append(listing)
                    except Exception as e:
                        logger.warning(f"Failed to parse vehicle data: {e}")
                        continue
                
                return listings
            else:
                logger.warning("No vehicles returned from Auto.dev API")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Auto.dev API: {e}")
            return []
    
    def get_vehicle_details(self, external_id: str) -> Optional[VehicleListing]:
        """Get detailed vehicle information from Auto.dev API."""
        try:
            response = self._make_request(f'listings/{external_id}')
            
            if response:
                return self._parse_vehicle_data(response)
            else:
                logger.warning(f"No vehicle details found for ID: {external_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting vehicle details from Auto.dev API: {e}")
            return None
    
    def _parse_vehicle_data(self, listing_data: Dict[str, Any]) -> Optional[VehicleListing]:
        """Parse Auto.dev API listing data into VehicleListing format."""
        try:
            # Auto.dev response has nested structure: vehicle data + retail listing data
            vehicle_info = listing_data.get('vehicle', {})
            retail_info = listing_data.get('retailListing', {})
            
            # Extract features from vehicle specifications
            features = []
            if 'specifications' in vehicle_info:
                specs = vehicle_info['specifications']
                if isinstance(specs, dict):
                    for category, spec_list in specs.items():
                        if isinstance(spec_list, list):
                            features.extend(spec_list)
            
            # Extract images from retail listing
            images = []
            if 'images' in retail_info:
                images = [img.get('url', '') for img in retail_info['images'] if isinstance(img, dict)]
            
            # Extract location information
            location = ""
            if 'city' in retail_info and 'state' in retail_info:
                location = f"{retail_info['city']}, {retail_info['state']}"
            elif 'dealership' in retail_info:
                dealer = retail_info['dealership']
                if 'city' in dealer and 'state' in dealer:
                    location = f"{dealer['city']}, {dealer['state']}"
            
            # Create VehicleListing object
            listing = VehicleListing(
                source="auto.dev",
                external_id=str(listing_data.get('id', listing_data.get('vin', ''))),
                make=vehicle_info.get('make', '').title(),
                model=vehicle_info.get('model', '').title(),
                year=int(vehicle_info.get('year', 0)) if vehicle_info.get('year') else 0,
                price=float(retail_info.get('price', 0)) if retail_info.get('price') else None,
                mileage=int(retail_info.get('miles', 0)) if retail_info.get('miles') else None,  # Fixed: mileage is in retailListing.miles
                fuel_type=vehicle_info.get('fuel', '').replace('_', ' ').title(),  # Fixed: field is 'fuel' not 'fuelType'
                transmission=vehicle_info.get('transmission', '').replace('_', ' ').title(),
                location=location,
                safety_rating=vehicle_info.get('safetyRating'),
                mpg_city=vehicle_info.get('mpgCity'),  # May not be available in API
                mpg_highway=vehicle_info.get('mpgHighway'),  # May not be available in API
                vin=vehicle_info.get('vin', ''),
                description=retail_info.get('description', ''),
                features=features[:10] if features else [],  # Limit to 10 features
                images=images[:5] if images else [],  # Limit to 5 images
                dealer_name=retail_info.get('dealer', ''),  # Fixed: dealer name is directly in retailListing.dealer
                dealer_phone=retail_info.get('phone', ''),  # May not be available
                listing_url=retail_info.get('vdp', ''),  # Fixed: URL is in retailListing.vdp
                listing_date=retail_info.get('listedDate', '')
            )
            
            return listing
            
        except Exception as e:
            logger.error(f"Error parsing Auto.dev vehicle data: {e}")
            return None
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """Make HTTP request to Auto.dev API with error handling."""
        try:
            url = f"{self.base_url}/{endpoint}"
            
            response = self.session.get(
                url,
                params=params,
                timeout=30
            )
            
            # Handle different response status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error("Auto.dev API authentication failed - check API key")
                return None
            elif response.status_code == 429:
                logger.warning("Auto.dev API rate limit exceeded")
                return None
            elif response.status_code >= 500:
                logger.error(f"Auto.dev API server error: {response.status_code}")
                return None
            else:
                logger.warning(f"Auto.dev API returned status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Auto.dev API request timed out")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Auto.dev API")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Auto.dev API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Auto.dev API request: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test if the API key and connection are working."""
        try:
            response = self._make_request('listings', {'limit': 1})
            return response is not None
        except Exception:
            return False