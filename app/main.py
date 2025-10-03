import streamlit as st
import sys
import os
from pathlib import Path

# Add the project root to Python path for proper imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.utils.config import load_config
    from app.ui.sidebar import render_sidebar
    from app.ui.results import render_results
    from app.ui.components import render_header, render_chat_interface
    from app.models.database import init_database, get_database_manager
except ImportError:
    # Fallback for direct imports
    from utils.config import load_config
    from ui.sidebar import render_sidebar
    from ui.results import render_results
    from ui.components import render_header, render_chat_interface
    from models.database import init_database, get_database_manager

# Page configuration
st.set_page_config(
    page_title="CarFinder - AI Car Shopping Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main Streamlit application entry point."""
    
    # Initialize configuration
    config = load_config()
    
    # Initialize database
    init_database()
    
    # Render header
    render_header()
    
    # Initialize session state
    if "preferences" not in st.session_state:
        st.session_state.preferences = {}
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "chat_mode" not in st.session_state:
        st.session_state.chat_mode = False
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # Main layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Sidebar for preferences
        preferences = render_sidebar()
        st.session_state.preferences = preferences
        
        # Chat mode toggle
        st.markdown("---")
        if st.button("🤖 Chat with AI Agent", use_container_width=True):
            st.session_state.chat_mode = not st.session_state.chat_mode
    
    with col2:
        if st.session_state.chat_mode:
            # Render chat interface
            render_chat_interface()
        else:
            # Search and recommend based on preferences
            if any(preferences.values()):
                # Use database search with fallback for advanced features
                try:
                    # Get database manager first (always works)
                    db_manager = get_database_manager()
                    
                    # Get basic search results
                    search_results = db_manager.search_vehicles_by_preferences(preferences, limit=20)
                    
                    if search_results:
                        # Try to use recommendation engine for scoring
                        try:
                            from recommendations.engine import RecommendationEngine
                            recommendation_engine = RecommendationEngine(config)
                            
                            # Convert to format expected by recommendation engine
                            vehicle_dicts = [{'vehicle': v.to_dict(), 'score': 1.0} for v in search_results]
                            recommendations = recommendation_engine.recommend(vehicle_dicts, preferences)
                            
                            # Render results with recommendations
                            render_results(recommendations, vehicle_dicts)
                            
                        except Exception as e:
                            st.info(f"Using basic search (recommendation engine unavailable: {e})")
                            # Simple results display
                            st.markdown(f"### 🔍 Found {len(search_results)} vehicles")
                            
                            for i, vehicle in enumerate(search_results, 1):
                                st.markdown(f"#### {i}. {vehicle.year} {vehicle.make} {vehicle.model}")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Price", f"${vehicle.price:,}")
                                with col2:
                                    st.metric("Mileage", f"{vehicle.mileage:,} miles")
                                with col3:
                                    if vehicle.mpg_city and vehicle.mpg_highway:
                                        st.metric("MPG", f"{vehicle.mpg_city}/{vehicle.mpg_highway}")
                                
                                st.write(f"**Fuel Type:** {vehicle.fuel_type}")
                                if vehicle.safety_rating:
                                    st.write(f"**Safety Rating:** {'⭐' * int(vehicle.safety_rating)} ({vehicle.safety_rating}/5)")
                                
                                if vehicle.description:
                                    with st.expander("Description"):
                                        st.write(vehicle.description)
                                
                                st.markdown("---")
                    else:
                        st.warning("No vehicles found matching your criteria.")
                        st.markdown("**Try adjusting your filters:**")
                        st.markdown("• Increase your budget range")
                        st.markdown("• Expand the year range")
                        st.markdown("• Consider different makes or fuel types")
                        
                except Exception as e:
                    st.error(f"Search failed: {e}")
                    st.markdown("Please try refreshing the page or adjusting your search criteria.")
            else:
                # Welcome message
                st.markdown("""
                ## Welcome to CarFinder! 🚗
                
                **Get personalized car recommendations powered by AI**
                
                ### How it works:
                1. **Set your preferences** in the sidebar (budget, make, features, etc.)
                2. **View recommendations** - get a curated shortlist and our top pick
                3. **Chat with our AI agent** for personalized guidance
                4. **Explore details** including safety ratings, recalls, and TCO estimates
                
                ### Features:
                - 🔍 **Smart Search**: RAG-powered semantic search
                - 🎯 **Personalized Recommendations**: AI-driven matching
                - 🛡️ **Safety First**: Recall checks and safety ratings
                - 💰 **Cost Analysis**: Total Cost of Ownership estimates
                - 🤖 **AI Agent**: Conversational car shopping assistant
                - 🔒 **Privacy Focused**: All processing done locally
                
                **Start by setting your preferences in the sidebar →**
                """)

if __name__ == "__main__":
    main()