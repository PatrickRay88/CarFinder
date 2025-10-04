"""
CarFinder AI - Vehicle Shopping Assistant with Live Data Integration
Enhanced with real-time vehicle listings from multiple sources.
"""

import streamlit as st
import sys
from pathlib import Path

# Add the app directory to Python path for imports
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

try:
    from utils.config import load_config, get_database_url
    from models.database import DatabaseManager
    from utils.simple_rag import SimpleRAG
    from agents.conversation import ConversationState, ConversationAgent
    import json
    import re
    from datetime import datetime
    import logging
    
    # Import vehicle data service with fixed imports
    from services.vehicle_data import VehicleDataService
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

class CarFinderAI:
    def __init__(self):
        self.config = load_config()
        database_url = get_database_url(self.config)
        self.db_manager = DatabaseManager(database_url)
        self.db_manager.init_database()  # Initialize database tables
        self.vehicle_service = VehicleDataService()
        self.rag = SimpleRAG(self.db_manager)
        self.conversation_agent = ConversationAgent(self.config)
        
        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'conversation' not in st.session_state:
            st.session_state.conversation = ConversationState()
        if 'preferences' not in st.session_state:
            st.session_state.preferences = {}
        if 'use_live_data' not in st.session_state:
            st.session_state.use_live_data = True  # Enable live data for real-time listings
    
    def render_header(self):
        """Render the application header with live data toggle."""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("🚗 CarFinder AI")
            st.markdown("*Your intelligent car shopping assistant with live market data*")
        
        with col2:
            # Data source status
            if st.button("📊 Data Sources"):
                self.show_data_source_status()
        
        with col3:
            # Live data toggle
            use_live = st.toggle("🌐 Live Data", value=st.session_state.use_live_data)
            if use_live != st.session_state.use_live_data:
                st.session_state.use_live_data = use_live
                st.rerun()
            
            # Show current mode
            if st.session_state.use_live_data:
                st.caption("🟢 Auto.dev API Active")
            else:
                st.caption("🔵 Local Database Only")
    
    def show_data_source_status(self):
        """Show data source status in a modal-like display."""
        with st.expander("🔍 Data Source Status", expanded=True):
            status = self.vehicle_service.get_data_source_status()
            
            # Local database status
            st.subheader("📱 Local Database")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Vehicles", status['local_database']['vehicle_count'])
            with col2:
                st.metric("Status", "✅ Active")
            
            # Live sources status
            st.subheader("🌐 Live Data Sources")
            live_stats = status['live_sources']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active Sources", live_stats['total_sources'])
            with col2:
                if st.button("🔄 Refresh Live Data"):
                    with st.spinner("Refreshing live data..."):
                        refresh_result = self.vehicle_service.refresh_live_data()
                        if refresh_result['success']:
                            st.success(f"✅ Added {refresh_result['new_listings']} new listings")
                        else:
                            st.error(f"❌ Error: {refresh_result['error']}")
            
            # Source details
            for source, details in live_stats['source_capabilities'].items():
                with st.container():
                    st.write(f"**{source}**")
                    api_status = "🔑 Configured" if details['has_api_key'] else "🆓 Open Source"
                    st.caption(f"{api_status} | {details['base_url']}")
    
    def extract_preferences_from_text(self, user_input: str) -> dict:
        """Extract vehicle preferences from natural language input."""
        preferences = {}
        text = user_input.lower()
        
        # Extract budget
        budget_patterns = [
            r'budget.*?(\d+(?:,\d+)*(?:\.\d+)?)[k]?',
            r'under.*?(\d+(?:,\d+)*(?:\.\d+)?)[k]?',
            r'max.*?(\d+(?:,\d+)*(?:\.\d+)?)[k]?',
            r'\$(\d+(?:,\d+)*(?:\.\d+)?)[k]?'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, text)
            if match:
                budget_str = match.group(1).replace(',', '')
                budget = float(budget_str)
                if 'k' in match.group(0) or budget < 1000:
                    budget *= 1000
                preferences['budget_max'] = budget
                break
        
        # Extract make/model
        makes = ['toyota', 'honda', 'ford', 'chevrolet', 'nissan', 'hyundai', 'kia', 'subaru', 'mazda', 'volkswagen', 'bmw', 'mercedes', 'audi', 'lexus', 'acura', 'infiniti', 'tesla', 'jeep', 'dodge', 'chrysler']
        for make in makes:
            if make in text:
                preferences['make'] = make.title()
                break
        
        # Extract fuel type
        if any(word in text for word in ['hybrid', 'electric', 'ev', 'prius']):
            if 'electric' in text or 'ev' in text or 'tesla' in text:
                preferences['fuel_type'] = 'Electric'
            else:
                preferences['fuel_type'] = 'Hybrid'
        
        # Extract year preferences
        year_match = re.search(r'(20\d{2})', text)
        if year_match:
            preferences['year_min'] = int(year_match.group(1))
        
        if any(word in text for word in ['new', 'newer', 'recent', 'latest']):
            preferences['year_min'] = 2020
        
        # Extract mileage preferences
        if any(word in text for word in ['low mileage', 'few miles', 'barely driven']):
            preferences['mileage_max'] = 30000
            
        # Extract specific mileage numbers
        mileage_match = re.search(r'under\s+(\d+(?:,\d+)*)\s*miles', text)
        if mileage_match:
            mileage_str = mileage_match.group(1).replace(',', '')
            preferences['mileage_max'] = int(mileage_str)
        
        # Extract vehicle type (CRITICAL for truck detection)
        vehicle_type_keywords = {
            'truck': ['truck', 'pickup', 'pickup truck', 'pick-up', 'f-150', 'silverado', 'ram', 'tacoma', 'tundra', 'sierra'],
            'suv': ['suv', 'sport utility', 'crossover', 'suburban', 'tahoe', 'explorer', 'pilot', 'highlander'],
            'sedan': ['sedan', 'car', 'four-door', '4-door'],
            'coupe': ['coupe', 'two-door', '2-door', 'sports car'],
            'hatchback': ['hatchback', 'hatch'],
            'wagon': ['wagon', 'estate']
        }
        
        for vehicle_type, keywords in vehicle_type_keywords.items():
            if any(keyword in text for keyword in keywords):
                preferences['vehicle_type'] = vehicle_type
                break
        
        # Debug logging
        if preferences:
            logger.info(f"Extracted preferences: {preferences}")
        
        return preferences
    
    def intelligent_vehicle_search(self, preferences: dict) -> list:
        """Perform intelligent vehicle search using hybrid data sources."""
        try:
            # Use the vehicle service for hybrid search
            search_results = self.vehicle_service.search_vehicles_hybrid(
                preferences, 
                use_live_data=st.session_state.use_live_data
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in intelligent search: {e}")
            return []
    
    def calculate_ai_score(self, vehicle: dict, preferences: dict) -> float:
        """Calculate AI compatibility score for a vehicle."""
        score = 0.0
        max_score = 100.0
        
        # Budget compatibility (30 points)
        if preferences.get('budget_max') and vehicle.get('price'):
            if vehicle['price'] <= preferences['budget_max']:
                budget_efficiency = 1 - (vehicle['price'] / preferences['budget_max'])
                score += budget_efficiency * 30
        
        # Vehicle type preference (25 points) - CRITICAL for truck vs sedan distinction
        if preferences.get('vehicle_type'):
            vehicle_type_requested = preferences['vehicle_type'].lower()
            vehicle_make = vehicle.get('make', '').lower()
            vehicle_model = vehicle.get('model', '').lower()
            
            # Check if vehicle matches requested type
            if vehicle_type_requested == 'truck':
                # Only truck-exclusive makes (Ram only makes trucks)
                truck_only_makes = ['ram']  
                # Truck-specific model keywords
                truck_models = ['f-150', 'f150', 'silverado', 'sierra', 'tacoma', 'tundra', 'ram', 'frontier', 'ranger', 'colorado', 'canyon', 'ridgeline', 'truck']
                
                # Check for truck-only makes OR truck-specific model keywords
                make_match = vehicle_make in truck_only_makes
                model_match = any(model in vehicle_model for model in truck_models)
                
                if make_match or model_match:
                    score += 25  # Big bonus for being the right vehicle type
                else:
                    score -= 15  # Penalty for being wrong vehicle type (sedan when asking for truck)
            elif vehicle_type_requested == 'suv':
                suv_models = ['suburban', 'tahoe', 'explorer', 'pilot', 'highlander', 'cr-v', 'rav4', 'escape', 'edge']
                if any(model in vehicle_model for model in suv_models):
                    score += 25
                else:
                    score -= 10
        
        # Log vehicle type matches for monitoring
        if preferences.get('vehicle_type') and score > 20:  # Only log high-scoring matches
            logger.info(f"High match: {preferences['vehicle_type']} preference → {vehicle.get('make')} {vehicle.get('model')} (Score: {score:.1f})")
        
        # Make preference (20 points)
        if preferences.get('make') and vehicle.get('make'):
            if vehicle['make'].lower() == preferences['make'].lower():
                score += 20
        
        # Fuel type preference (15 points)
        if preferences.get('fuel_type') and vehicle.get('fuel_type'):
            if vehicle['fuel_type'] == preferences['fuel_type']:
                score += 15
        
        # Year preference (15 points)
        if preferences.get('year_min') and vehicle.get('year'):
            if vehicle['year'] >= preferences['year_min']:
                year_bonus = min(15, (vehicle['year'] - preferences['year_min'] + 1) * 3)
                score += year_bonus
        
        # Mileage preference (10 points)
        if vehicle.get('mileage'):
            mileage_max = preferences.get('mileage_max', 100000)
            if vehicle['mileage'] <= mileage_max:
                mileage_efficiency = 1 - (vehicle['mileage'] / mileage_max)
                score += mileage_efficiency * 10
        
        # Safety rating bonus (10 points)
        if vehicle.get('safety_rating'):
            score += (vehicle['safety_rating'] / 5) * 10
        
        # Data completeness penalty - penalize vehicles with missing critical data
        missing_data_penalty = 0
        critical_fields = ['mileage', 'mpg_city', 'mpg_highway', 'year']
        
        for field in critical_fields:
            if not vehicle.get(field):
                missing_data_penalty += 10  # 10 point penalty per missing field (stricter)
        
        # Additional penalty for vehicles missing multiple critical fields
        missing_count = sum(1 for field in critical_fields if not vehicle.get(field))
        if missing_count >= 3:
            missing_data_penalty += 15  # Extra penalty for very incomplete data
        
        # Apply penalty but don't let score go below 0
        score = max(0, score - missing_data_penalty)
        
        # Log data completeness issues for high-scoring but incomplete vehicles
        if missing_data_penalty > 0:  # Log all vehicles with missing data
            missing_fields = [field for field in critical_fields if not vehicle.get(field)]
            logger.info(f"Data completeness check: {vehicle.get('make')} {vehicle.get('model')} - Missing: {missing_fields} (Penalty: -{missing_data_penalty}, Final Score: {score:.1f})")
        
        return min(score, max_score)
    
    def render_vehicle_card(self, vehicle: dict, ai_score: float = None, is_top_pick: bool = False):
        """Render a beautiful vehicle card with enhanced information."""
        
        # Determine card style based on type
        if is_top_pick:
            card_style = """
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            """
        else:
            card_style = """
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            """
        
        with st.container():
            st.markdown(f"""
            <div style="
                {card_style}
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                margin: 10px 0;
                border: 1px solid rgba(255,255,255,0.2);
            ">
            </div>
            """, unsafe_allow_html=True)
            
            # Header with title and source
            col1, col2 = st.columns([3, 1])
            with col1:
                title = f"**{vehicle.get('year', 'N/A')} {vehicle.get('make', 'Unknown')} {vehicle.get('model', 'Unknown')}**"
                if is_top_pick:
                    st.markdown(f"## 🏆 {title}")
                    st.markdown("**🎯 AI TOP RECOMMENDATION**")
                else:
                    st.markdown(f"### {title}")
            
            with col2:
                # Show data source
                source = vehicle.get('source', 'local')
                if source in ['cars.com', 'autotrader', 'cargurus', 'auto.dev']:
                    st.markdown("**🌐 LIVE**")
                    st.caption(f"from {source}")
                else:
                    st.markdown("**📱 LOCAL**")
                
                if ai_score is not None:
                    st.metric("🤖 AI Match", f"{ai_score:.0f}%")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if vehicle.get('price'):
                    budget_max = st.session_state.preferences.get('budget_max', 0)
                    if budget_max > 0:
                        savings = budget_max - vehicle['price']
                        if savings > 5000:
                            st.metric("💰 Price", f"${vehicle['price']:,}", f"${savings:,} saved!")
                        else:
                            st.metric("💰 Price", f"${vehicle['price']:,}")
                    else:
                        st.metric("💰 Price", f"${vehicle['price']:,}")
                else:
                    st.metric("💰 Price", "Contact Dealer")
            
            with col2:
                if vehicle.get('mileage'):
                    st.metric("🚗 Mileage", f"{vehicle['mileage']:,} mi")
                else:
                    st.metric("🚗 Mileage", "N/A")
            
            with col3:
                mpg_display = "N/A"
                if vehicle.get('mpg_city') and vehicle.get('mpg_highway'):
                    mpg_display = f"{vehicle['mpg_city']}/{vehicle['mpg_highway']}"
                elif vehicle.get('fuel_type') == 'Electric':
                    mpg_display = "Electric"
                st.metric("⛽ MPG", mpg_display)
            
            with col4:
                safety = vehicle.get('safety_rating')
                if safety:
                    stars = "⭐" * int(safety)
                    st.metric("🛡️ Safety", stars)
                else:
                    st.metric("🛡️ Safety", "Not Rated")
            
            # Description and features
            if vehicle.get('description'):
                st.markdown(f"**📝 Description:** {vehicle['description']}")
            
            if vehicle.get('features'):
                features = vehicle['features']
                if isinstance(features, str):
                    try:
                        features = json.loads(features.replace("'", '"'))
                    except:
                        features = [features]
                
                if features:
                    st.markdown("**✨ Key Features:**")
                    # Display features in a nice grid
                    feature_cols = st.columns(3)
                    for i, feature in enumerate(features[:6]):  # Show max 6 features
                        with feature_cols[i % 3]:
                            st.markdown(f"• {feature}")
            
            # Contact information for live listings
            if vehicle.get('dealer_name') or vehicle.get('listing_url'):
                with st.expander("📞 Contact & Details"):
                    if vehicle.get('dealer_name'):
                        st.write(f"**Dealer:** {vehicle['dealer_name']}")
                    if vehicle.get('dealer_phone'):
                        st.write(f"**Phone:** {vehicle['dealer_phone']}")
                    if vehicle.get('listing_url'):
                        st.markdown(f"[🔗 View Full Listing]({vehicle['listing_url']})")
                    if vehicle.get('location'):
                        st.write(f"**Location:** {vehicle['location']}")
    
    def process_message(self, user_input: str):
        """Process user message and generate AI response with vehicle recommendations."""
        # Use conversation agent for intelligent preference extraction
        agent_response = self.conversation_agent.process_message(user_input, st.session_state.conversation)
        
        # Extract preferences from conversation agent
        agent_preferences = agent_response.get('extracted_preferences', {})
        conversation_preferences = self.conversation_agent.extract_preferences_from_conversation(
            st.session_state.conversation.conversation_history
        )
        
        # Also use the basic extraction as fallback
        basic_preferences = self.extract_preferences_from_text(user_input)
        
        # Combine all preference sources (conversation agent takes priority)
        new_preferences = {**basic_preferences, **agent_preferences, **conversation_preferences}
        
        # Update stored preferences
        st.session_state.preferences.update(new_preferences)
        preferences = st.session_state.preferences
        
        # Add to chat history
        st.session_state.chat_history.append({
            'user': user_input,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
        # Generate response
        response = ""
        search_results = []
        
        if preferences:
            # Perform intelligent search
            search_results = self.intelligent_vehicle_search(preferences)
            
            if search_results:
                # Calculate AI scores for all results
                scored_results = []
                for vehicle in search_results:
                    ai_score = self.calculate_ai_score(vehicle, preferences)
                    scored_results.append((vehicle, ai_score))
                
                # Filter out vehicles with very low scores (less than 5% compatibility)
                # These are likely vehicles with missing data or wrong type
                min_score_threshold = 5.0
                original_count = len(scored_results)
                scored_results = [(vehicle, score) for vehicle, score in scored_results if score >= min_score_threshold]
                filtered_count = original_count - len(scored_results)
                
                if filtered_count > 0:
                    logger.info(f"Filtered out {filtered_count} vehicles with scores below {min_score_threshold}% (likely incomplete data)")
                
                # Sort by AI score
                scored_results.sort(key=lambda x: x[1], reverse=True)
                
                if not scored_results:
                    response = "❌ **I found vehicles matching your search criteria, but they all had incomplete data (missing mileage, MPG, etc.) so I filtered them out for quality.**\n\n"
                    response += "💡 **Try:**\n"
                    response += "- Adjusting your search criteria\n"
                    response += "- Looking for different makes/models\n"
                    response += "- Expanding your budget or mileage range\n\n"
                    response += "The live data sources sometimes have incomplete listings - this filtering protects you from making decisions without key information!"
                    return response, []
                
                # Generate contextual response
                top_vehicle = scored_results[0][0]
                top_score = scored_results[0][1]
                
                data_source_info = ""
                if st.session_state.use_live_data:
                    live_count = sum(1 for v, _ in scored_results if v.get('source') in ['cars.com', 'autotrader', 'cargurus'])
                    if live_count > 0:
                        data_source_info = f" I found {live_count} live listings from current market data!"
                
                quality_info = ""
                if filtered_count > 0:
                    quality_info = f" (filtered out {filtered_count} with incomplete data for quality)"
                
                response = f"🎯 **Perfect! I found {len(scored_results)} high-quality vehicles matching your criteria{quality_info}.{data_source_info}**\n\n"
                response += f"**🏆 My #1 recommendation** is the **{top_vehicle.get('year')} {top_vehicle.get('make')} {top_vehicle.get('model')}** "
                response += f"with a {top_score:.0f}% AI compatibility match!\n\n"
                
                if preferences.get('budget_max') and top_vehicle.get('price'):
                    savings = preferences['budget_max'] - top_vehicle['price']
                    if savings > 5000:
                        price_context = f"**${top_vehicle['price']:,}** *(${savings:,} under budget - great value!)*"
                    elif savings > 0:
                        price_context = f"**${top_vehicle['price']:,}** *(within budget)*"
                    else:
                        price_context = f"**${top_vehicle['price']:,}** *(slightly over budget, but worth considering)*"
                    response += f"💰 **Price:** {price_context}\n"
                
                if top_vehicle.get('mileage'):
                    response += f"🚗 **Mileage:** {top_vehicle['mileage']:,} miles\n"
                
                if top_vehicle.get('mpg_city') and top_vehicle.get('mpg_highway'):
                    response += f"⛽ **Fuel Economy:** {top_vehicle['mpg_city']}/{top_vehicle['mpg_highway']} MPG\n"
                elif top_vehicle.get('fuel_type') == 'Electric':
                    response += f"⚡ **Fuel Type:** Electric (no gas needed!)\n"
                
                response += f"\n📍 **Why it's perfect for you:**\n"
                
                # Add personalized reasoning
                if preferences.get('fuel_type') and top_vehicle.get('fuel_type') == preferences['fuel_type']:
                    response += f"• Matches your {preferences['fuel_type'].lower()} preference\n"
                if preferences.get('make') and top_vehicle.get('make', '').lower() == preferences['make'].lower():
                    response += f"• You specifically mentioned {preferences['make']}\n"
                if preferences.get('budget_max') and top_vehicle.get('price') and top_vehicle['price'] <= preferences['budget_max']:
                    response += f"• Fits within your ${preferences['budget_max']:,} budget\n"
                
                response += f"\n🔍 **See all {len(search_results)} results below** - I've ranked them by how well they match your needs!\n\n"
                response += "❓ **Questions? Want details?** Ask me anything about these vehicles - maintenance costs, insurance estimates, feature comparisons, or how they'd fit your specific lifestyle!"
            else:
                response = "🤔 **Hmm, I'm having trouble finding the perfect match** for your specific requirements in our current inventory.\n\n"
                response += "**💡 Here are a few suggestions:**\n"
                response += "• Try expanding your budget range\n"
                response += "• Consider different makes or models\n"
                response += "• Adjust your year or mileage preferences\n\n"
                if not st.session_state.use_live_data:
                    response += "💡 **Tip:** Enable 'Live Data' above to search current market listings from multiple sources!\n\n"
                response += "Tell me more about what's most important to you, and I'll help find alternatives!"
        
        else:
            # Initial greeting or clarification
            response = "👋 **Hello! I'm your AI car shopping assistant.** I can help you find the perfect vehicle based on your needs and budget.\n\n"
            response += "**To get started, tell me:**\n"
            response += "• Your budget range\n"
            response += "• Preferred make or model (if any)\n" 
            response += "• Type of driving you do most\n"
            response += "• Any specific features you want\n\n"
            response += "*For example: 'I need a reliable SUV under $30,000 for family trips' or 'Looking for a fuel-efficient car around $25k'*"
        
        # Ensure we always have a valid vehicles list for return
        final_vehicles = []
        if 'scored_results' in locals() and scored_results:
            final_vehicles = scored_results
        
        # Add response to chat history
        st.session_state.chat_history.append({
            'assistant': response,
            'timestamp': datetime.now().strftime('%H:%M'),
            'vehicles': final_vehicles
        })
        
        return response, final_vehicles
    
    def render_chat_interface(self):
        """Render the conversational chat interface."""
        st.markdown("### 💬 Chat with Your AI Assistant")
        
        # Chat history
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history:
                if 'user' in message:
                    with st.chat_message("user"):
                        st.write(message['user'])
                        
                elif 'assistant' in message:
                    with st.chat_message("assistant"):
                        st.markdown(message['assistant'])
                        
                        # Show vehicles if any
                        if 'vehicles' in message and message['vehicles']:
                            st.markdown("---")
                            
                            # Show top pick first
                            if message['vehicles']:
                                top_vehicle, top_score = message['vehicles'][0]
                                self.render_vehicle_card(top_vehicle, top_score, is_top_pick=True)
                                
                                # Show other results
                                if len(message['vehicles']) > 1:
                                    st.markdown("### 🔍 Other Great Options")
                                    for vehicle, score in message['vehicles'][1:6]:  # Show up to 5 more
                                        self.render_vehicle_card(vehicle, score)
        
        # Input for new messages
        if prompt := st.chat_input("Ask me about cars, describe what you're looking for..."):
            with st.chat_message("user"):
                st.write(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("🤖 Analyzing your preferences and searching..."):
                    response, vehicles = self.process_message(prompt)
                    st.markdown(response)
                    
                    # Display vehicles if any found
                    if vehicles:
                        # Show top recommendation
                        if len(vehicles) > 0:
                            st.markdown("### 🏆 Top Recommendation")
                            self.render_vehicle_card(vehicles[0][0], vehicles[0][1])
                        
                        # Show other options
                        if len(vehicles) > 1:
                            st.markdown("### 🔍 Other Great Options")
                            for vehicle, score in vehicles[1:5]:  # Show up to 4 more
                                self.render_vehicle_card(vehicle, score)
    
    def render_sidebar(self):
        """Render sidebar with preferences and controls."""
        st.sidebar.markdown("## 🎛️ Search Preferences")
        
        # Current preferences display
        if st.session_state.preferences:
            with st.sidebar.expander("📋 Current Preferences", expanded=True):
                for key, value in st.session_state.preferences.items():
                    if key == 'budget_max':
                        st.write(f"💰 **Budget:** ${value:,.0f}")
                    elif key == 'make':
                        st.write(f"🚗 **Make:** {value}")
                    elif key == 'fuel_type':
                        st.write(f"⛽ **Fuel:** {value}")
                    elif key == 'year_min':
                        st.write(f"📅 **Min Year:** {value}")
                    elif key == 'mileage_max':
                        st.write(f"🚗 **Max Mileage:** {value:,}")
        
        # Manual preference controls
        st.sidebar.markdown("### 🎯 Quick Filters")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🗑️ Clear All"):
                st.session_state.preferences = {}
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Data source info
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Data Sources")
        
        if st.session_state.use_live_data:
            live_status = "🟢 **Auto.dev API**"
            st.sidebar.markdown(f"**Mode:** {live_status}")
            st.sidebar.caption("Real-time vehicle data")
        else:
            live_status = "� **Local Database**"
            st.sidebar.markdown(f"**Mode:** {live_status}")
            st.sidebar.caption("Curated sample data")
        
        # Quick stats
        try:
            status = self.vehicle_service.get_data_source_status()
            st.sidebar.metric("Local Vehicles", status['local_database']['vehicle_count'])
            
            if st.session_state.use_live_data:
                st.sidebar.metric("Live Sources", status['live_sources']['total_sources'])
                # Check if Auto.dev API key is configured
                if self.config.get('auto_dev_api_key'):
                    st.sidebar.success("✅ Auto.dev API Ready")
                else:
                    st.sidebar.warning("⚠️ Auto.dev API key needed")
            
        except Exception as e:
            st.sidebar.error(f"Error loading stats: {e}")

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="CarFinder AI - Live Data",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better appearance
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize and run the application
    app = CarFinderAI()
    
    # Render components
    app.render_header()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        app.render_chat_interface()
    
    with col2:
        app.render_sidebar()

if __name__ == "__main__":
    main()