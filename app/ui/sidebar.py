"""Sidebar component for user preferences input."""
import streamlit as st
from typing import Dict, Any, List

def render_sidebar() -> Dict[str, Any]:
    """Render the preferences sidebar and return user selections."""
    
    st.sidebar.markdown("## 🎯 Your Preferences")
    
    preferences = {}
    
    # Budget section
    st.sidebar.markdown("### 💰 Budget")
    budget_max = st.sidebar.number_input(
        "Maximum Budget ($)",
        min_value=0,
        max_value=200000,
        value=30000,
        step=1000,
        key="pref_budget_max"
    )
    preferences['budget_max'] = budget_max if budget_max > 0 else None
    
    # Vehicle basics
    st.sidebar.markdown("### 🚗 Vehicle Type")
    
    make = st.sidebar.selectbox(
        "Preferred Make",
        options=["", "Toyota", "Honda", "Ford", "Chevrolet", "BMW", "Mercedes-Benz", 
                "Audi", "Volkswagen", "Subaru", "Mazda", "Hyundai", "Kia", "Other"],
        key="pref_make"
    )
    preferences['make'] = make if make else None
    
    year_range = st.sidebar.slider(
        "Model Year Range",
        min_value=2010,
        max_value=2024,
        value=(2018, 2024),
        key="pref_year_range"
    )
    preferences['min_year'] = year_range[0]
    preferences['max_year'] = year_range[1]
    
    # Fuel and efficiency
    st.sidebar.markdown("### ⛽ Fuel & Efficiency")
    
    fuel_type = st.sidebar.selectbox(
        "Fuel Type",
        options=["", "Gasoline", "Hybrid", "Electric", "Diesel"],
        key="pref_fuel_type"
    )
    preferences['fuel_type'] = fuel_type if fuel_type else None
    
    min_mpg = st.sidebar.number_input(
        "Minimum MPG (combined)",
        min_value=0,
        max_value=50,
        value=0,
        key="pref_min_mpg"
    )
    preferences['min_mpg'] = min_mpg if min_mpg > 0 else None
    
    # Mileage
    st.sidebar.markdown("### 🛣️ Mileage")
    max_mileage = st.sidebar.number_input(
        "Maximum Mileage",
        min_value=0,
        max_value=200000,
        value=100000,
        step=10000,
        key="pref_max_mileage"
    )
    preferences['max_mileage'] = max_mileage if max_mileage > 0 else None
    
    # Features
    st.sidebar.markdown("### ✨ Desired Features")
    
    features = st.sidebar.multiselect(
        "Important Features",
        options=[
            "Backup Camera", "Bluetooth", "Navigation", "Sunroof", 
            "Leather Seats", "Heated Seats", "All-Wheel Drive", 
            "Automatic Transmission", "Keyless Entry", "Premium Audio"
        ],
        key="pref_features"
    )
    preferences['desired_features'] = features
    
    # Safety
    st.sidebar.markdown("### 🛡️ Safety")
    min_safety_rating = st.sidebar.select_slider(
        "Minimum Safety Rating",
        options=[0, 1, 2, 3, 4, 5],
        value=4,
        format_func=lambda x: f"{x} stars" if x > 0 else "No preference",
        key="pref_min_safety"
    )
    preferences['min_safety_rating'] = min_safety_rating if min_safety_rating > 0 else None
    
    # Location
    st.sidebar.markdown("### 📍 Location")
    location = st.sidebar.text_input(
        "Preferred Location (city, state)",
        placeholder="e.g., San Francisco, CA",
        key="pref_location"
    )
    preferences['location'] = location if location else None
    
    if location:
        radius = st.sidebar.selectbox(
            "Search Radius (miles)",
            options=[25, 50, 100, 200, 500],
            index=2,  # Default to 100 miles
            key="pref_radius"
        )
        preferences['radius'] = radius
    else:
        preferences['radius'] = None
    
    # Priority weights
    st.sidebar.markdown("### ⚖️ What matters most?")
    st.sidebar.markdown("Rank your priorities:")
    
    price_weight = st.sidebar.slider("Price Importance", 0.0, 1.0, 0.3, 0.1, key="weight_price")
    reliability_weight = st.sidebar.slider("Reliability Importance", 0.0, 1.0, 0.4, 0.1, key="weight_reliability")
    fuel_weight = st.sidebar.slider("Fuel Efficiency Importance", 0.0, 1.0, 0.2, 0.1, key="weight_fuel")
    safety_weight = st.sidebar.slider("Safety Importance", 0.0, 1.0, 0.1, 0.1, key="weight_safety")
    
    preferences['weights'] = {
        'price': price_weight,
        'reliability': reliability_weight,
        'fuel_efficiency': fuel_weight,
        'safety': safety_weight
    }
    
    # Search button
    st.sidebar.markdown("---")
    if st.sidebar.button("🔍 Search Vehicles", use_container_width=True):
        st.session_state['trigger_search'] = True
    
    # Reset button
    if st.sidebar.button("🔄 Reset Preferences", use_container_width=True):
        # Clear all preference keys from session state
        keys_to_clear = [k for k in st.session_state.keys() if k.startswith('pref_') or k.startswith('weight_')]
        for key in keys_to_clear:
            del st.session_state[key]
        st.rerun()
    
    return preferences

def render_preference_summary(preferences: Dict[str, Any]):
    """Render a summary of current preferences."""
    active_prefs = []
    
    if preferences.get('budget_max'):
        active_prefs.append(f"Budget: ≤${preferences['budget_max']:,}")
    if preferences.get('make'):
        active_prefs.append(f"Make: {preferences['make']}")
    if preferences.get('fuel_type'):
        active_prefs.append(f"Fuel: {preferences['fuel_type']}")
    if preferences.get('min_year') and preferences.get('max_year'):
        active_prefs.append(f"Year: {preferences['min_year']}-{preferences['max_year']}")
    
    if active_prefs:
        st.sidebar.markdown("**Current filters:**")
        for pref in active_prefs[:3]:  # Show max 3
            st.sidebar.markdown(f"• {pref}")
        if len(active_prefs) > 3:
            st.sidebar.markdown(f"• ... and {len(active_prefs) - 3} more")