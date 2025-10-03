import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd

# Add paths for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

# Page configuration
st.set_page_config(
    page_title="CarFinder - AI Car Shopping Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_simple_config():
    """Load basic configuration."""
    return {
        'database_path': 'data/carfinder.db',
        'max_results': 20,
        'project_root': project_root
    }

def render_simple_header():
    """Render the application header."""
    st.markdown("""
    # 🚗 CarFinder
    ### AI-Powered Car Shopping Assistant
    
    Find your perfect car match with personalized AI recommendations.
    """)

def render_simple_sidebar():
    """Render a basic preferences sidebar."""
    st.sidebar.markdown("## 🎯 Your Preferences")
    
    preferences = {}
    
    # Budget section
    st.sidebar.markdown("### 💰 Budget")
    budget_max = st.sidebar.number_input(
        "Maximum Budget ($)",
        min_value=0,
        max_value=200000,
        value=30000,
        step=1000
    )
    preferences['budget_max'] = budget_max if budget_max > 0 else None
    
    # Vehicle basics
    st.sidebar.markdown("### 🚗 Vehicle Type")
    make = st.sidebar.selectbox(
        "Preferred Make",
        options=["", "Toyota", "Honda", "Ford", "Chevrolet", "BMW", "Mercedes-Benz", 
                "Audi", "Volkswagen", "Subaru", "Mazda", "Hyundai", "Kia", "Other"]
    )
    preferences['make'] = make if make else None
    
    year_range = st.sidebar.slider(
        "Model Year Range",
        min_value=2010,
        max_value=2024,
        value=(2018, 2024)
    )
    preferences['min_year'] = year_range[0]
    preferences['max_year'] = year_range[1]
    
    # Fuel type
    st.sidebar.markdown("### ⛽ Fuel & Efficiency")
    fuel_type = st.sidebar.selectbox(
        "Fuel Type",
        options=["", "Gasoline", "Hybrid", "Electric", "Diesel"]
    )
    preferences['fuel_type'] = fuel_type if fuel_type else None
    
    return preferences

def get_sample_vehicles():
    """Get sample vehicle data."""
    return [
        {
            'id': 1, 'make': 'Toyota', 'model': 'Camry', 'year': 2022, 'price': 28500,
            'mileage': 15000, 'fuel_type': 'Gasoline', 'mpg_city': 28, 'mpg_highway': 39,
            'safety_rating': 5, 'features': ['Backup Camera', 'Bluetooth', 'Keyless Entry'],
            'description': 'Excellent condition Toyota Camry with low mileage.'
        },
        {
            'id': 2, 'make': 'Honda', 'model': 'Accord', 'year': 2021, 'price': 26800,
            'mileage': 22000, 'fuel_type': 'Gasoline', 'mpg_city': 30, 'mpg_highway': 38,
            'safety_rating': 5, 'features': ['Backup Camera', 'Bluetooth', 'Navigation'],
            'description': 'Reliable Honda Accord with excellent safety ratings.'
        },
        {
            'id': 3, 'make': 'Toyota', 'model': 'Prius', 'year': 2023, 'price': 32000,
            'mileage': 8000, 'fuel_type': 'Hybrid', 'mpg_city': 57, 'mpg_highway': 56,
            'safety_rating': 4, 'features': ['Backup Camera', 'Navigation', 'Premium Audio'],
            'description': 'Nearly new Toyota Prius hybrid with exceptional fuel economy.'
        },
        {
            'id': 4, 'make': 'Honda', 'model': 'CR-V', 'year': 2022, 'price': 31500,
            'mileage': 18000, 'fuel_type': 'Gasoline', 'mpg_city': 28, 'mpg_highway': 34,
            'safety_rating': 5, 'features': ['Backup Camera', 'All-Wheel Drive', 'Heated Seats'],
            'description': 'Versatile Honda CR-V SUV with AWD and excellent safety.'
        },
        {
            'id': 5, 'make': 'Tesla', 'model': 'Model 3', 'year': 2022, 'price': 45000,
            'mileage': 12000, 'fuel_type': 'Electric', 'mpg_city': 120, 'mpg_highway': 115,
            'safety_rating': 5, 'features': ['Navigation', 'Premium Audio', 'Keyless Entry'],
            'description': 'Tesla Model 3 electric sedan with autopilot features.'
        }
    ]

def filter_vehicles(vehicles, preferences):
    """Filter vehicles based on user preferences."""
    filtered = vehicles.copy()
    
    if preferences.get('budget_max'):
        filtered = [v for v in filtered if v['price'] <= preferences['budget_max']]
    
    if preferences.get('make'):
        filtered = [v for v in filtered if v['make'].lower() == preferences['make'].lower()]
    
    if preferences.get('min_year'):
        filtered = [v for v in filtered if v['year'] >= preferences['min_year']]
    
    if preferences.get('max_year'):
        filtered = [v for v in filtered if v['year'] <= preferences['max_year']]
    
    if preferences.get('fuel_type'):
        filtered = [v for v in filtered if v['fuel_type'].lower() == preferences['fuel_type'].lower()]
    
    return filtered

def render_vehicle_card(vehicle, rank=None):
    """Render a vehicle card."""
    with st.container():
        if rank:
            st.subheader(f"{rank}. {vehicle['year']} {vehicle['make']} {vehicle['model']}")
        else:
            st.subheader(f"{vehicle['year']} {vehicle['make']} {vehicle['model']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Price", f"${vehicle['price']:,}")
        with col2:
            st.metric("Mileage", f"{vehicle['mileage']:,} miles")
        with col3:
            if vehicle['mpg_city'] and vehicle['mpg_highway']:
                st.metric("MPG", f"{vehicle['mpg_city']}/{vehicle['mpg_highway']}")
        
        st.write(f"**Fuel Type:** {vehicle['fuel_type']}")
        if vehicle['safety_rating']:
            st.write(f"**Safety Rating:** {'⭐' * vehicle['safety_rating']} ({vehicle['safety_rating']}/5)")
        
        if vehicle.get('features'):
            with st.expander("Features"):
                for feature in vehicle['features']:
                    st.write(f"✓ {feature}")
        
        st.write(f"**Description:** {vehicle['description']}")
        st.markdown("---")

def main():
    """Main application."""
    
    # Render header
    render_simple_header()
    
    # Initialize session state
    if "preferences" not in st.session_state:
        st.session_state.preferences = {}
    
    # Main layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Sidebar for preferences
        preferences = render_simple_sidebar()
        st.session_state.preferences = preferences
    
    with col2:
        # Get sample vehicles (in a real app, this would come from database)
        all_vehicles = get_sample_vehicles()
        
        if any(preferences.values()):
            # Filter vehicles based on preferences
            filtered_vehicles = filter_vehicles(all_vehicles, preferences)
            
            if filtered_vehicles:
                st.markdown(f"### 🎯 Found {len(filtered_vehicles)} vehicles matching your criteria")
                
                # Show top recommendation
                if filtered_vehicles:
                    st.markdown("#### 🏆 Top Recommendation")
                    render_vehicle_card(filtered_vehicles[0])
                
                # Show other results
                if len(filtered_vehicles) > 1:
                    st.markdown("#### 📋 Other Great Options")
                    for i, vehicle in enumerate(filtered_vehicles[1:], 2):
                        render_vehicle_card(vehicle, rank=i)
            
            else:
                st.warning("🔍 No vehicles found matching your criteria. Try adjusting your preferences.")
                st.markdown("**Suggestions:**")
                st.markdown("• Increase your budget range")
                st.markdown("• Expand the year range") 
                st.markdown("• Consider different makes or fuel types")
        
        else:
            # Welcome message
            st.markdown("""
            ## Welcome to CarFinder! 🚗
            
            **Get personalized car recommendations powered by AI**
            
            ### How it works:
            1. **Set your preferences** in the sidebar (budget, make, features, etc.)
            2. **View recommendations** - get a curated shortlist and our top pick
            3. **Explore details** including safety ratings and features
            
            ### Sample Features:
            - 🔍 **Smart Search**: Filter by budget, make, year, fuel type
            - 🎯 **Personalized Recommendations**: AI-driven matching
            - 🛡️ **Safety Focus**: Safety ratings display
            - 📊 **Vehicle Comparison**: Compare multiple options
            
            **Start by setting your preferences in the sidebar →**
            """)
            
            # Show all available vehicles as examples
            st.markdown("### 📋 Sample Vehicles Available")
            for i, vehicle in enumerate(all_vehicles, 1):
                render_vehicle_card(vehicle, rank=i)

if __name__ == "__main__":
    main()