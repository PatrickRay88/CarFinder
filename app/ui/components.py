"""Streamlit UI components for CarFinder."""
import streamlit as st
from typing import Dict, List, Any, Optional

def render_header():
    """Render the application header."""
    st.markdown("""
    # 🚗 CarFinder
    ### AI-Powered Car Shopping Assistant
    
    Find your perfect car match with personalized AI recommendations.
    """)

def render_vehicle_card(vehicle: Dict[str, Any], show_score: bool = False, score: float = None):
    """Render a vehicle card with details."""
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"{vehicle['year']} {vehicle['make']} {vehicle['model']}")
            
            # Basic info
            info_cols = st.columns(3)
            with info_cols[0]:
                st.metric("Price", f"${vehicle['price']:,.0f}" if vehicle['price'] else "N/A")
            with info_cols[1]:
                st.metric("Mileage", f"{vehicle['mileage']:,} miles" if vehicle['mileage'] else "N/A")
            with info_cols[2]:
                if vehicle['mpg_city'] and vehicle['mpg_highway']:
                    st.metric("MPG", f"{vehicle['mpg_city']}/{vehicle['mpg_highway']}")
                else:
                    st.metric("MPG", "N/A")
            
            # Additional details
            if vehicle['fuel_type']:
                st.write(f"**Fuel Type:** {vehicle['fuel_type']}")
            if vehicle['transmission']:
                st.write(f"**Transmission:** {vehicle['transmission']}")
            if vehicle['location']:
                st.write(f"**Location:** {vehicle['location']}")
            
            # Safety rating
            if vehicle['safety_rating']:
                st.write(f"**Safety Rating:** {'⭐' * int(vehicle['safety_rating'])} ({vehicle['safety_rating']}/5)")
        
        with col2:
            if show_score and score is not None:
                st.metric("Match Score", f"{score:.1%}")
            
            # Action buttons
            import hashlib
            import time
            import random
            # Create a more unique key using multiple factors
            unique_suffix = str(int(time.time() * 1000000)) + str(random.randint(1000, 9999))
            vehicle_id = vehicle.get('id', hashlib.md5(str(vehicle).encode()).hexdigest()[:8])
            
            if st.button(f"View Details", key=f"details_{vehicle_id}_{unique_suffix}"):
                st.session_state[f"show_details_{vehicle_id}"] = True
            
            if vehicle.get('vin'):
                if st.button(f"Check Recalls", key=f"recalls_{vehicle_id}_{unique_suffix}"):
                    # Implement recall check
                    st.info("Recall check feature coming soon!")
        
        # Features
        if vehicle.get('features'):
            with st.expander("Features"):
                features = vehicle['features'] if isinstance(vehicle['features'], list) else []
                if features:
                    # Display features in columns
                    feature_cols = st.columns(3)
                    for i, feature in enumerate(features):
                        with feature_cols[i % 3]:
                            st.write(f"✓ {feature}")
                else:
                    st.write("No features listed")
        
        # Description
        if vehicle.get('description'):
            with st.expander("Description"):
                st.write(vehicle['description'])
        
        st.markdown("---")

def render_recommendation_summary(recommendations: List[Dict[str, Any]], preferences: Dict[str, Any]):
    """Render recommendation summary and insights."""
    if not recommendations:
        st.warning("No vehicles found matching your criteria. Try adjusting your preferences.")
        return
    
    st.markdown("### 🎯 Your Personalized Recommendations")
    
    # Top pick
    top_pick = recommendations[0]
    with st.container():
        st.markdown("#### 🏆 Our Top Pick for You")
        render_vehicle_card(top_pick['vehicle'], show_score=True, score=top_pick['score'])
        
        # Explanation
        if 'explanation' in top_pick:
            st.info(f"**Why we recommend this:** {top_pick['explanation']}")
    
    # Other recommendations
    if len(recommendations) > 1:
        st.markdown("#### 📋 Other Great Options")
        
        for i, rec in enumerate(recommendations[1:], 1):
            with st.expander(f"{i+1}. {rec['vehicle']['year']} {rec['vehicle']['make']} {rec['vehicle']['model']} (Score: {rec['score']:.1%})"):
                render_vehicle_card(rec['vehicle'], show_score=True, score=rec['score'])
                if 'explanation' in rec:
                    st.write(f"**Match reason:** {rec['explanation']}")

def render_comparison_tool(vehicles: List[Dict[str, Any]]):
    """Render side-by-side vehicle comparison."""
    if len(vehicles) < 2:
        return
    
    st.markdown("### 🔍 Vehicle Comparison")
    
    # Select vehicles to compare
    vehicle_options = {f"{v['year']} {v['make']} {v['model']}": v for v in vehicles}
    selected = st.multiselect(
        "Select vehicles to compare (max 3):",
        options=list(vehicle_options.keys()),
        max_selections=3
    )
    
    if len(selected) >= 2:
        comparison_data = []
        for name in selected:
            vehicle = vehicle_options[name]
            comparison_data.append({
                "Vehicle": name,
                "Price": f"${vehicle['price']:,.0f}" if vehicle['price'] else "N/A",
                "Mileage": f"{vehicle['mileage']:,}" if vehicle['mileage'] else "N/A",
                "MPG City": vehicle['mpg_city'] or "N/A",
                "MPG Highway": vehicle['mpg_highway'] or "N/A",
                "Fuel Type": vehicle['fuel_type'] or "N/A",
                "Safety Rating": vehicle['safety_rating'] or "N/A",
            })
        
        # Display comparison table
        import pandas as pd
        df = pd.DataFrame(comparison_data)
        st.table(df.set_index("Vehicle"))

def render_chat_interface():
    """Render the conversational chat interface."""
    st.markdown("### 🤖 Chat with Your Car Shopping Assistant")
    
    # Chat history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # Display chat history
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Tell me about your ideal car..."):
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Display user message
        st.chat_message("user").write(user_input)
        
        # Generate AI response (placeholder for now)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # This would integrate with the actual conversation agent
                response = generate_chat_response(user_input, st.session_state.conversation_history)
                st.write(response)
                
                # Add AI response to history
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })

def generate_chat_response(user_input: str, conversation_history: List[Dict[str, str]]) -> str:
    """Generate chat response (placeholder implementation)."""
    # This is a placeholder - in the full implementation, this would use
    # the ConversationAgent with Ollama/LangGraph
    
    responses = [
        "I'd be happy to help you find the perfect car! Can you tell me more about your budget and what type of driving you do most?",
        "That sounds like a great choice! Based on what you've told me, I'd recommend looking at vehicles with good fuel efficiency and safety ratings.",
        "Let me search for vehicles that match your criteria. I'll consider your budget, preferred features, and driving needs.",
        "I found some excellent options for you! Would you like me to explain why each vehicle might be a good fit for your needs?",
    ]
    
    import random
    return random.choice(responses)

def render_filters_applied(preferences: Dict[str, Any]):
    """Show applied filters in a compact format."""
    applied_filters = []
    
    if preferences.get('budget_max'):
        applied_filters.append(f"Budget: ≤${preferences['budget_max']:,}")
    if preferences.get('make'):
        applied_filters.append(f"Make: {preferences['make']}")
    if preferences.get('fuel_type'):
        applied_filters.append(f"Fuel: {preferences['fuel_type']}")
    if preferences.get('min_year'):
        applied_filters.append(f"Year: ≥{preferences['min_year']}")
    
    if applied_filters:
        st.markdown("**Active Filters:** " + " | ".join(applied_filters))

def render_loading_placeholder():
    """Render loading placeholder while searching."""
    with st.spinner("🔍 Searching for your perfect car match..."):
        st.empty()

def render_no_results_message(preferences: Dict[str, Any]):
    """Render message when no results are found."""
    st.warning("🔍 No vehicles found matching your criteria.")
    
    suggestions = [
        "Try increasing your budget range",
        "Consider different makes or models", 
        "Expand your year range",
        "Check if your fuel type preference is too restrictive"
    ]
    
    st.markdown("**Suggestions to find more options:**")
    for suggestion in suggestions:
        st.markdown(f"• {suggestion}")
    
    if st.button("Clear All Filters"):
        # Clear session state preferences
        for key in list(st.session_state.keys()):
            if key.startswith('pref_'):
                del st.session_state[key]
        st.experimental_rerun()