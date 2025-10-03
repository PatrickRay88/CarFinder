"""Results display component for CarFinder."""
import streamlit as st
from typing import Dict, List, Any
from .components import render_vehicle_card, render_recommendation_summary, render_comparison_tool

def render_results(recommendations: List[Dict[str, Any]], search_results: List[Dict[str, Any]]):
    """Render search results and recommendations."""
    
    if not recommendations and not search_results:
        render_no_results()
        return
    
    # Results summary
    st.markdown(f"### 📊 Found {len(search_results)} vehicles matching your criteria")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🎯 Recommendations", "📋 All Results", "🔍 Compare"])
    
    with tab1:
        if recommendations:
            render_recommendation_summary(recommendations, st.session_state.get('preferences', {}))
        else:
            st.info("No personalized recommendations available. Check the 'All Results' tab to see matching vehicles.")
    
    with tab2:
        render_all_results(search_results)
    
    with tab3:
        if search_results:
            render_comparison_tool([result['vehicle'] if isinstance(result, dict) and 'vehicle' in result else result for result in search_results])
        else:
            st.info("No vehicles available for comparison.")

def render_all_results(search_results: List[Dict[str, Any]]):
    """Render all search results in a grid."""
    
    if not search_results:
        st.info("No vehicles found matching your criteria.")
        return
    
    # Sorting options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"Showing {len(search_results)} vehicles")
    
    with col2:
        sort_by = st.selectbox(
            "Sort by:",
            options=["price_asc", "price_desc", "year_desc", "mileage_asc", "mpg_desc"],
            format_func=lambda x: {
                "price_asc": "Price (Low to High)",
                "price_desc": "Price (High to Low)", 
                "year_desc": "Year (Newest First)",
                "mileage_asc": "Mileage (Low to High)",
                "mpg_desc": "MPG (Best First)"
            }.get(x, x)
        )
    
    # Sort results
    sorted_results = sort_results(search_results, sort_by)
    
    # Display results
    for i, result in enumerate(sorted_results):
        # Handle both direct vehicle dicts and recommendation dicts
        if isinstance(result, dict) and 'vehicle' in result:
            vehicle = result['vehicle']
            score = result.get('score')
        else:
            vehicle = result
            score = None
        
        render_vehicle_card(vehicle, show_score=score is not None, score=score)
        
        # Add some spacing every few results
        if (i + 1) % 3 == 0 and i < len(sorted_results) - 1:
            st.markdown("---")

def sort_results(results: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
    """Sort search results by the specified criteria."""
    
    def get_vehicle_data(result):
        if isinstance(result, dict) and 'vehicle' in result:
            return result['vehicle']
        return result
    
    if sort_by == "price_asc":
        return sorted(results, key=lambda x: get_vehicle_data(x).get('price', float('inf')))
    elif sort_by == "price_desc":
        return sorted(results, key=lambda x: get_vehicle_data(x).get('price', 0), reverse=True)
    elif sort_by == "year_desc":
        return sorted(results, key=lambda x: get_vehicle_data(x).get('year', 0), reverse=True)
    elif sort_by == "mileage_asc":
        return sorted(results, key=lambda x: get_vehicle_data(x).get('mileage', float('inf')))
    elif sort_by == "mpg_desc":
        return sorted(results, key=lambda x: (
            get_vehicle_data(x).get('mpg_city', 0) + get_vehicle_data(x).get('mpg_highway', 0)
        ) / 2, reverse=True)
    
    return results

def render_no_results():
    """Render message when no results found."""
    st.markdown("### 🔍 No Results Found")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        We couldn't find any vehicles matching your current criteria.
        
        **Try these suggestions:**
        - Increase your budget range
        - Expand the year range
        - Consider different makes or fuel types
        - Reduce the number of required features
        - Check if your location filter is too specific
        """)
        
        if st.button("Clear All Filters"):
            # Clear session state
            keys_to_clear = [k for k in st.session_state.keys() if k.startswith('pref_')]
            for key in keys_to_clear:
                del st.session_state[key]
            st.experimental_rerun()
    
    with col2:
        st.markdown("""
        **Popular Searches:**
        - Budget under $25,000
        - Hybrid vehicles
        - SUVs with AWD
        - Cars with high safety ratings
        """)

def render_vehicle_details_modal(vehicle: Dict[str, Any]):
    """Render detailed vehicle information in a modal-like container."""
    
    st.markdown(f"## {vehicle['year']} {vehicle['make']} {vehicle['model']}")
    
    # Main details in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 💰 Pricing")
        st.metric("Listed Price", f"${vehicle['price']:,}" if vehicle['price'] else "N/A")
        
        if vehicle['price']:
            # Rough TCO estimate (placeholder)
            estimated_monthly = vehicle['price'] / 60  # 5-year financing estimate
            st.metric("Est. Monthly Payment", f"${estimated_monthly:,.0f}")
    
    with col2:
        st.markdown("### 🚗 Specifications")
        st.write(f"**Year:** {vehicle['year']}")
        st.write(f"**Mileage:** {vehicle['mileage']:,} miles" if vehicle['mileage'] else "**Mileage:** N/A")
        st.write(f"**Fuel Type:** {vehicle['fuel_type']}" if vehicle['fuel_type'] else "**Fuel Type:** N/A")
        st.write(f"**Transmission:** {vehicle['transmission']}" if vehicle['transmission'] else "**Transmission:** N/A")
    
    with col3:
        st.markdown("### ⭐ Ratings & Efficiency")
        if vehicle['safety_rating']:
            st.metric("Safety Rating", f"{vehicle['safety_rating']}/5 ⭐")
        
        if vehicle['mpg_city'] and vehicle['mpg_highway']:
            st.metric("MPG", f"{vehicle['mpg_city']} city / {vehicle['mpg_highway']} hwy")
    
    # Features
    if vehicle.get('features'):
        st.markdown("### ✨ Features")
        features = vehicle['features'] if isinstance(vehicle['features'], list) else []
        if features:
            # Display in a nice grid
            cols = st.columns(3)
            for i, feature in enumerate(features):
                with cols[i % 3]:
                    st.write(f"✅ {feature}")
    
    # Description
    if vehicle.get('description'):
        st.markdown("### 📝 Description")
        st.write(vehicle['description'])
    
    # Location
    if vehicle.get('location'):
        st.markdown("### 📍 Location")
        st.write(vehicle['location'])
    
    # Action buttons
    st.markdown("### 🎯 Next Steps")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save to Favorites"):
            st.success("Added to favorites!")
    
    with col2:
        if st.button("🔍 Check Recalls"):
            if vehicle.get('vin'):
                st.info("Recall check feature coming soon!")
            else:
                st.warning("VIN not available for recall check.")
    
    with col3:
        if st.button("📊 Calculate TCO"):
            st.info("Total Cost of Ownership calculator coming soon!")