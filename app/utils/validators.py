"""Input validation utilities for CarFinder."""
from typing import Any, Dict, List, Optional
import re

def validate_budget(budget: Any) -> Optional[float]:
    """Validate budget input."""
    if budget is None or budget == "":
        return None
    
    try:
        budget_float = float(budget)
        if budget_float < 0:
            return None
        if budget_float > 1000000:  # Reasonable upper limit
            return None
        return budget_float
    except (ValueError, TypeError):
        return None

def validate_year(year: Any) -> Optional[int]:
    """Validate year input."""
    if year is None or year == "":
        return None
    
    try:
        year_int = int(year)
        if year_int < 1900 or year_int > 2030:
            return None
        return year_int
    except (ValueError, TypeError):
        return None

def validate_mileage(mileage: Any) -> Optional[int]:
    """Validate mileage input."""
    if mileage is None or mileage == "":
        return None
    
    try:
        mileage_int = int(mileage)
        if mileage_int < 0 or mileage_int > 500000:  # Reasonable limits
            return None
        return mileage_int
    except (ValueError, TypeError):
        return None

def validate_mpg(mpg: Any) -> Optional[int]:
    """Validate MPG input."""
    if mpg is None or mpg == "":
        return None
    
    try:
        mpg_int = int(mpg)
        if mpg_int < 5 or mpg_int > 150:  # Reasonable limits
            return None
        return mpg_int
    except (ValueError, TypeError):
        return None

def validate_safety_rating(rating: Any) -> Optional[float]:
    """Validate safety rating input."""
    if rating is None or rating == "":
        return None
    
    try:
        rating_float = float(rating)
        if rating_float < 0 or rating_float > 5:
            return None
        return rating_float
    except (ValueError, TypeError):
        return None

def validate_vin(vin: str) -> Optional[str]:
    """Validate VIN (Vehicle Identification Number)."""
    if not vin:
        return None
    
    # Basic VIN validation (17 characters, alphanumeric except I, O, Q)
    vin = vin.upper().strip()
    if len(vin) != 17:
        return None
    
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
        return None
    
    return vin

def validate_make(make: str) -> Optional[str]:
    """Validate vehicle make."""
    if not make or not make.strip():
        return None
    
    make = make.strip().title()
    
    # List of known makes for validation
    known_makes = {
        'Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz',
        'Audi', 'Volkswagen', 'Subaru', 'Mazda', 'Hyundai', 'Kia',
        'Nissan', 'Tesla', 'Jeep', 'Ram', 'GMC', 'Cadillac', 'Lexus',
        'Acura', 'Infiniti', 'Lincoln', 'Buick', 'Chrysler', 'Dodge',
        'Mitsubishi', 'Volvo', 'Jaguar', 'Land Rover', 'Porsche',
        'Maserati', 'Ferrari', 'Lamborghini', 'Bentley', 'Rolls-Royce'
    }
    
    # Allow unknown makes but with reasonable length
    if len(make) > 50:
        return None
    
    return make

def validate_fuel_type(fuel_type: str) -> Optional[str]:
    """Validate fuel type."""
    if not fuel_type or not fuel_type.strip():
        return None
    
    fuel_type = fuel_type.strip().title()
    
    valid_fuel_types = {
        'Gasoline', 'Hybrid', 'Electric', 'Diesel', 'CNG', 'Ethanol'
    }
    
    if fuel_type not in valid_fuel_types:
        return None
    
    return fuel_type

def validate_features(features: List[str]) -> List[str]:
    """Validate and clean feature list."""
    if not features:
        return []
    
    valid_features = []
    for feature in features:
        if isinstance(feature, str) and feature.strip():
            # Clean and limit length
            clean_feature = feature.strip()[:100]  # Max 100 chars per feature
            valid_features.append(clean_feature)
    
    # Limit total number of features
    return valid_features[:20]

def sanitize_text_input(text: str, max_length: int = 1000) -> str:
    """Sanitize text input for database storage."""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = str(text).strip()
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def validate_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean user preferences."""
    cleaned = {}
    
    # Budget validation
    if 'budget_max' in preferences:
        cleaned['budget_max'] = validate_budget(preferences['budget_max'])
    
    if 'budget_min' in preferences:
        cleaned['budget_min'] = validate_budget(preferences['budget_min'])
    
    # Year validation
    if 'min_year' in preferences:
        cleaned['min_year'] = validate_year(preferences['min_year'])
    
    if 'max_year' in preferences:
        cleaned['max_year'] = validate_year(preferences['max_year'])
    
    # Make validation
    if 'make' in preferences:
        cleaned['make'] = validate_make(preferences['make'])
    
    # Fuel type validation
    if 'fuel_type' in preferences:
        cleaned['fuel_type'] = validate_fuel_type(preferences['fuel_type'])
    
    # Mileage validation
    if 'max_mileage' in preferences:
        cleaned['max_mileage'] = validate_mileage(preferences['max_mileage'])
    
    # MPG validation
    if 'min_mpg' in preferences:
        cleaned['min_mpg'] = validate_mpg(preferences['min_mpg'])
    
    # Safety rating validation
    if 'min_safety_rating' in preferences:
        cleaned['min_safety_rating'] = validate_safety_rating(preferences['min_safety_rating'])
    
    # Features validation
    if 'desired_features' in preferences:
        cleaned['desired_features'] = validate_features(preferences['desired_features'])
    
    # Location validation (simple text)
    if 'location' in preferences:
        location = preferences['location']
        if location and isinstance(location, str):
            cleaned['location'] = sanitize_text_input(location, 200)
    
    # Query validation
    if 'query' in preferences:
        query = preferences['query']
        if query and isinstance(query, str):
            cleaned['query'] = sanitize_text_input(query, 500)
    
    # Remove None values
    return {k: v for k, v in cleaned.items() if v is not None}