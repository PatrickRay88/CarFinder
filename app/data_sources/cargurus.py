"""
CarGurus API integration for real-time vehicle listings.
"""

from typing import Dict, List, Optional, Any
import logging
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from data_sources.base import VehicleDataSource, VehicleListing

logger = logging.getLogger(__name__)

class CarGurusAPI(VehicleDataSource):
    """
    CarGurus API integration.
    Note: Mock implementation for demonstration purposes.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key)
        self.base_url = "https://api.cargurus.com/v1"
        
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
        """Search vehicles on CarGurus."""
        
        # Mock data showcasing different vehicle types - includes budget options
        mock_listings = [
            # Budget-friendly options under $15k
            VehicleListing(
                source="cargurus",
                external_id="cg_budget_001",
                make="Ford",
                model="Focus",
                year=2014,
                price=8900.00,
                mileage=125000,
                fuel_type="Gasoline",
                transmission="Automatic",
                location="Seattle, WA",
                safety_rating=4,
                mpg_city=26,
                mpg_highway=36,
                vin="1FADP3K23EL123456",
                description="2014 Ford Focus - affordable and reliable transportation",
                features=["Bluetooth", "Power Steering", "Air Conditioning", "AM/FM Radio"],
                images=["https://example.com/focus1.jpg"],
                dealer_name="Northwest Auto",
                dealer_phone="(555) 666-7777",
                listing_url="https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity=budget001",
                listing_date="2024-10-03"
            ),
            VehicleListing(
                source="cargurus",
                external_id="cg_budget_002",
                make="Kia",
                model="Forte",
                year=2017,
                price=14200.00,
                mileage=75000,
                fuel_type="Gasoline",
                transmission="CVT",
                location="Seattle, WA",
                safety_rating=4,
                mpg_city=31,
                mpg_highway=41,
                vin="KNAFK4A61H5123456",
                description="2017 Kia Forte - low mileage with remaining factory warranty",
                features=["Backup Camera", "Bluetooth", "USB Port", "Keyless Entry", "Cruise Control"],
                images=["https://example.com/forte1.jpg"],
                dealer_name="Pacific Kia",
                dealer_phone="(555) 777-8888",
                listing_url="https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity=budget002",
                listing_date="2024-10-02"
            ),
            # Premium options
            VehicleListing(
                source="cargurus",
                external_id="cg_001",
                make="Tesla",
                model="Model 3",
                year=2022,
                price=39900.00,
                mileage=12000,
                fuel_type="Electric",
                transmission="Single-Speed",
                location="San Francisco, CA",
                safety_rating=5,
                mpg_city=None,  # Electric vehicles don't have traditional MPG
                mpg_highway=None,
                vin="5YJ3E1EA8NF123456",
                description="Tesla Model 3 Long Range with Autopilot and Premium Interior",
                features=["Autopilot", "Premium Interior", "Glass Roof", "Mobile Connector", "Supercharging"],
                images=["https://example.com/tesla_1.jpg"],
                dealer_name="Tesla San Francisco",
                dealer_phone="(555) 567-8901",
                listing_url="https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity=123456",
                listing_date="2024-10-02"
            ),
            VehicleListing(
                source="cargurus",
                external_id="cg_002",
                make="Subaru",
                model="Outback",
                year=2021,
                price=31500.00,
                mileage=25000,
                fuel_type="Gasoline",
                transmission="CVT",
                location="Seattle, WA",
                safety_rating=5,
                mpg_city=26,
                mpg_highway=33,
                vin="4S4BTAFC5M3123456",
                description="Subaru Outback Premium with EyeSight Safety Suite",
                features=["EyeSight", "All-Wheel Drive", "Roof Rails", "Power Liftgate", "Heated Seats"],
                images=["https://example.com/outback_1.jpg"],
                dealer_name="Subaru of Seattle",
                dealer_phone="(555) 678-9012",
                listing_url="https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity=234567",
                listing_date="2024-09-29"
            ),
            VehicleListing(
                source="cargurus", 
                external_id="cg_003",
                make="Jeep",
                model="Wrangler",
                year=2020,
                price=38750.00,
                mileage=40000,
                fuel_type="Gasoline",
                transmission="Manual",
                location="Phoenix, AZ",
                safety_rating=3,
                mpg_city=17,
                mpg_highway=25,
                vin="1C4HJXAG2LW123456",
                description="Jeep Wrangler Unlimited Sport with removable doors and roof",
                features=["4WD", "Removable Doors", "Fold-Down Windshield", "Rock Rails", "Tow Hooks"],
                images=["https://example.com/jeep_1.jpg"],
                dealer_name="Desert Jeep",
                dealer_phone="(555) 789-0123",
                listing_url="https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity=345678",
                listing_date="2024-09-27"
            )
        ]
        
        # Apply filters
        filtered_listings = []
        for listing in mock_listings:
            if make and listing.make.lower() != make.lower():
                continue
            if model and listing.model.lower() != model.lower():
                continue
            if price_min and listing.price < price_min:
                continue
            if price_max and listing.price > price_max:
                continue
            if year_min and listing.year < year_min:
                continue
            if year_max and listing.year > year_max:
                continue
            if mileage_max and listing.mileage > mileage_max:
                continue
                
            filtered_listings.append(listing)
            
        return filtered_listings[:limit]
    
    def get_vehicle_details(self, external_id: str) -> Optional[VehicleListing]:
        """Get detailed vehicle information from CarGurus."""
        if external_id == "cg_001":
            return VehicleListing(
                source="cargurus",
                external_id=external_id,
                make="Tesla",
                model="Model 3",
                year=2022,
                price=39900.00,
                mileage=12000,
                fuel_type="Electric",
                transmission="Single-Speed",
                location="San Francisco, CA",
                safety_rating=5,
                mpg_city=None,
                mpg_highway=None,
                vin="5YJ3E1EA8NF123456",
                description="Tesla Model 3 Long Range AWD with Full Self-Driving capability. Premium white interior with glass roof.",
                features=["Autopilot", "Full Self-Driving", "Premium Interior", "Glass Roof", "Mobile Connector", "Supercharging", "Over-the-Air Updates"],
                images=["https://example.com/tesla_1.jpg", "https://example.com/tesla_2.jpg", "https://example.com/tesla_interior.jpg"],
                dealer_name="Tesla San Francisco",
                dealer_phone="(555) 567-8901",
                listing_url="https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity=123456",
                listing_date="2024-10-02"
            )
        return None