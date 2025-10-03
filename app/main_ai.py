"""
AI-First CarFinder: GenAI-powered conversational car shopping assistant
Uses RAG, natural language understanding, and contextual recommendations
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

from models.database import get_database_manager
from utils.config import load_config
from utils.simple_rag import SimpleRAG

# Page configuration
st.set_page_config(
    page_title="CarFinder AI - Intelligent Car Shopping",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide the filter sidebar
)

class CarFinderAI:
    """AI-powered car shopping assistant."""
    
    def __init__(self):
        self.config = load_config()
        self.db_manager = get_database_manager()
        self.rag_system = SimpleRAG(self.db_manager)
        self.conversation_history = st.session_state.get('conversation_history', [])
        self.user_profile = st.session_state.get('user_profile', {})
        
    def extract_preferences_from_text(self, user_input: str) -> dict:
        """Extract car preferences from natural language using AI."""
        preferences = {}
        user_input_lower = user_input.lower()
        
        # Budget extraction
        import re
        budget_patterns = [
            r'under (\d+)k', r'less than (\d+)k', r'below (\d+)k',
            r'under \$?(\d+,?\d+)', r'less than \$?(\d+,?\d+)', r'below \$?(\d+,?\d+)',
            r'budget.*?(\d+)k', r'afford.*?(\d+)k', r'spend.*?(\d+)k'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                budget = match.group(1).replace(',', '')
                if 'k' in pattern:
                    preferences['budget_max'] = int(budget) * 1000
                else:
                    preferences['budget_max'] = int(budget)
                break
        
        # Vehicle type/size extraction
        size_keywords = {
            'compact': ['compact', 'small', 'city car', 'hatchback'],
            'sedan': ['sedan', 'four door', '4 door', 'family car'],
            'suv': ['suv', 'crossover', 'utility', 'bigger', 'spacious', 'family'],
            'truck': ['truck', 'pickup', 'work vehicle'],
            'sports': ['sports', 'fast', 'performance', 'sporty', 'coupe']
        }
        
        for size_type, keywords in size_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                preferences['vehicle_type'] = size_type
                break
        
        # Make preferences
        makes = ['toyota', 'honda', 'ford', 'chevrolet', 'bmw', 'mercedes', 'audi', 
                'volkswagen', 'subaru', 'mazda', 'hyundai', 'kia', 'nissan', 'tesla']
        
        for make in makes:
            if make in user_input_lower:
                preferences['make'] = make.title()
                break
        
        # Fuel type preferences
        fuel_keywords = {
            'electric': ['electric', 'ev', 'battery', 'tesla', 'plug-in'],
            'hybrid': ['hybrid', 'prius', 'eco', 'fuel efficient', 'green'],
            'gasoline': ['gas', 'gasoline', 'regular', 'conventional']
        }
        
        for fuel_type, keywords in fuel_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                preferences['fuel_type'] = fuel_type.title()
                break
        
        # Priority extraction
        priorities = {
            'reliability': ['reliable', 'dependable', 'last long', 'maintenance'],
            'fuel_economy': ['fuel efficient', 'gas mileage', 'mpg', 'economical'],
            'safety': ['safe', 'safety', 'family', 'protection', 'crash'],
            'performance': ['fast', 'powerful', 'acceleration', 'performance'],
            'luxury': ['luxury', 'premium', 'comfortable', 'features']
        }
        
        user_priorities = []
        for priority, keywords in priorities.items():
            if any(keyword in user_input_lower for keyword in keywords):
                user_priorities.append(priority)
        
        if user_priorities:
            preferences['priorities'] = user_priorities
        
        return preferences
    
    def intelligent_vehicle_search(self, preferences: dict, user_context: str = "") -> list:
        """AI-powered vehicle search with RAG and contextual understanding."""
        
        # Use RAG system for semantic search
        rag_results = self.rag_system.semantic_search(user_context, preferences)
        
        # If RAG finds good matches, use those
        if rag_results and len(rag_results) >= 3:
            # Enhance RAG results with additional AI scoring
            enhanced_results = []
            for result in rag_results:
                vehicle = result['vehicle']
                base_score = result['score']
                
                # Add AI-driven enhancements to the score
                ai_boost = self.calculate_ai_score(vehicle, preferences, user_context)
                combined_score = (base_score * 0.6) + (ai_boost * 0.4)
                
                enhanced_results.append({
                    'vehicle': vehicle,
                    'score': combined_score,
                    'reasoning': f"{result['relevance']} • {self.generate_recommendation_reasoning(vehicle, preferences)}"
                })
            
            # Re-sort by combined score
            enhanced_results.sort(key=lambda x: x['score'], reverse=True)
            return enhanced_results[:10]
        
        # Fallback to traditional filtering + AI scoring
        else:
            search_params = {}
            
            if preferences.get('budget_max'):
                search_params['max_price'] = preferences['budget_max']
            
            if preferences.get('make'):
                search_params['make'] = preferences['make']
            
            if preferences.get('fuel_type'):
                search_params['fuel_type'] = preferences['fuel_type']
            
            # Get candidate vehicles
            vehicles = self.db_manager.search_vehicles(**search_params, limit=20)
            
            if not vehicles:
                return []
            
            # AI-powered scoring and ranking
            scored_vehicles = []
            
            for vehicle in vehicles:
                score = self.calculate_ai_score(vehicle, preferences, user_context)
                scored_vehicles.append({
                    'vehicle': vehicle,
                    'score': score,
                    'reasoning': self.generate_recommendation_reasoning(vehicle, preferences)
                })
            
            # Sort by AI score
            scored_vehicles.sort(key=lambda x: x['score'], reverse=True)
            
            return scored_vehicles[:10]  # Return top 10 AI-curated recommendations
    
    def calculate_ai_score(self, vehicle, preferences: dict, user_context: str) -> float:
        """Calculate AI-driven compatibility score for a vehicle."""
        score = 0.0
        
        # Base score from price fit
        if preferences.get('budget_max'):
            price_fit = min(1.0, preferences['budget_max'] / vehicle.price)
            score += price_fit * 0.3
        else:
            score += 0.3  # No budget constraint
        
        # Priority-based scoring
        priorities = preferences.get('priorities', [])
        
        if 'reliability' in priorities:
            # Toyota, Honda = high reliability
            if vehicle.make.lower() in ['toyota', 'honda']:
                score += 0.25
            elif vehicle.make.lower() in ['ford', 'chevrolet']:
                score += 0.15
            else:
                score += 0.1
        
        if 'fuel_economy' in priorities:
            if vehicle.fuel_type == 'Hybrid':
                score += 0.25
            elif vehicle.fuel_type == 'Electric':
                score += 0.30
            elif vehicle.mpg_city and vehicle.mpg_city > 30:
                score += 0.20
            else:
                score += 0.05
        
        if 'safety' in priorities:
            if vehicle.safety_rating and vehicle.safety_rating >= 5:
                score += 0.20
            elif vehicle.safety_rating and vehicle.safety_rating >= 4:
                score += 0.15
            else:
                score += 0.05
        
        if 'luxury' in priorities:
            luxury_makes = ['bmw', 'mercedes-benz', 'audi', 'lexus']
            if vehicle.make.lower() in luxury_makes:
                score += 0.25
            else:
                score += 0.05
        
        # Year/age factor
        current_year = 2025
        age_factor = max(0, (current_year - vehicle.year + 1) / 10)  # Newer is better
        score += (1 - age_factor) * 0.1
        
        # Mileage factor  
        if vehicle.mileage < 20000:
            score += 0.15
        elif vehicle.mileage < 50000:
            score += 0.10
        else:
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    def generate_recommendation_reasoning(self, vehicle, preferences: dict) -> str:
        """Generate AI explanation for why this vehicle is recommended."""
        reasons = []
        
        # Budget fit
        if preferences.get('budget_max'):
            if vehicle.price <= preferences['budget_max'] * 0.8:
                reasons.append(f"Well within your ${preferences['budget_max']:,} budget")
            elif vehicle.price <= preferences['budget_max']:
                reasons.append(f"Fits your ${preferences['budget_max']:,} budget")
        
        # Priority matches
        priorities = preferences.get('priorities', [])
        
        if 'reliability' in priorities:
            if vehicle.make.lower() in ['toyota', 'honda']:
                reasons.append("Excellent reliability track record")
        
        if 'fuel_economy' in priorities:
            if vehicle.fuel_type == 'Hybrid':
                reasons.append("Hybrid technology for superior fuel economy")
            elif vehicle.fuel_type == 'Electric':
                reasons.append("Zero emissions electric powertrain")
            elif vehicle.mpg_city and vehicle.mpg_city > 30:
                reasons.append(f"Excellent {vehicle.mpg_city} city MPG")
        
        if 'safety' in priorities:
            if vehicle.safety_rating and vehicle.safety_rating >= 5:
                reasons.append("Top 5-star safety rating")
        
        # Vehicle-specific highlights
        if vehicle.year >= 2022:
            reasons.append("Recent model with latest features")
        
        if vehicle.mileage < 20000:
            reasons.append("Low mileage, like-new condition")
        
        return " • ".join(reasons) if reasons else "Good overall value and features"

def main():
    """Main AI-powered CarFinder application."""
    
    # Initialize AI assistant
    car_ai = CarFinderAI()
    
    # Header
    st.markdown("""
    # 🤖 CarFinder AI
    ### Your Intelligent Car Shopping Assistant
    
    **Tell me what you're looking for in natural language, and I'll find the perfect vehicles for you.**
    
    *No filters, no forms - just describe your needs and let AI do the work.*
    """)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your AI car shopping assistant. Tell me about what kind of car you're looking for - your budget, needs, preferences, or any specific requirements. I'll find and recommend the best vehicles for you based on our current inventory."}
        ]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Describe the car you're looking for..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process with AI
        with st.chat_message("assistant"):
            with st.spinner("🤖 Analyzing your needs and searching vehicles..."):
                
                # Extract preferences using AI
                preferences = car_ai.extract_preferences_from_text(prompt)
                
                # Get AI-curated vehicle recommendations
                recommendations = car_ai.intelligent_vehicle_search(preferences, prompt)
                
                if recommendations:
                    # Analyze the search to provide contextual intro
                    if preferences.get('budget_max'):
                        budget_text = f"within your ${preferences['budget_max']:,} budget"
                    else:
                        budget_text = "from our inventory"
                    
                    st.markdown(f"### 🎯 Perfect Match Found!")
                    st.success(f"I've analyzed {budget_text} and found **{len(recommendations)} vehicles** perfectly tailored to your needs!")
                    
                    # Showcase the #1 AI Pick prominently
                    top_pick = recommendations[0]
                    vehicle = top_pick['vehicle']
                    score = top_pick['score']
                    reasoning = top_pick['reasoning']
                    
                    # Top Pick Card with gradient background
                    st.markdown("#### 🏆 My #1 AI Recommendation")
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 20px;
                            border-radius: 12px;
                            color: white;
                            margin: 15px 0;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                        ">
                            <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px;">
                                🚗 {vehicle.year} {vehicle.make} {vehicle.model}
                            </h3>
                            <p style="margin: 0; font-size: 16px; opacity: 0.9;">
                                AI Match Score: <strong>{score:.0%}</strong> • Perfect Choice for You!
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Top pick metrics in clean layout
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if preferences.get('budget_max'):
                            savings = preferences['budget_max'] - vehicle.price
                            if savings > 5000:
                                st.metric("💰 Price", f"${vehicle.price:,}", f"${savings:,} saved!")
                            else:
                                st.metric("💰 Price", f"${vehicle.price:,}")
                        else:
                            st.metric("💰 Price", f"${vehicle.price:,}")
                    
                    with col2:
                        mileage_label = "🚗 Mileage"
                        if vehicle.mileage < 15000:
                            st.metric(mileage_label, f"{vehicle.mileage:,}", "Like New!")
                        elif vehicle.mileage < 30000:
                            st.metric(mileage_label, f"{vehicle.mileage:,}", "Low Miles")
                        else:
                            st.metric(mileage_label, f"{vehicle.mileage:,}")
                    
                    with col3:
                        if vehicle.mpg_city and vehicle.mpg_highway:
                            mpg_delta = "Excellent!" if vehicle.mpg_city > 30 else None
                            st.metric("⛽ Fuel Economy", f"{vehicle.mpg_city}/{vehicle.mpg_highway} MPG", mpg_delta)
                        else:
                            st.metric("⛽ Fuel Type", vehicle.fuel_type)
                    
                    with col4:
                        if vehicle.safety_rating:
                            safety_delta = "Top Rated!" if vehicle.safety_rating >= 5 else "Excellent" if vehicle.safety_rating >= 4 else None
                            st.metric("🛡️ Safety", f"{vehicle.safety_rating}/5 ⭐", safety_delta)
                    
                    # Top pick reasoning in an attractive info box
                    st.markdown("**✨ Why This is Perfect for You:**")
                    st.info(reasoning)
                    
                    if vehicle.description:
                        with st.expander("📋 Full Vehicle Details"):
                            st.write(vehicle.description)
                    
                    # Show other recommendations as compact cards
                    if len(recommendations) > 1:
                        st.markdown("---")
                        st.markdown("### 🎯 Other Great Options")
                        
                        for i, rec in enumerate(recommendations[1:3], 2):  # Show next 2
                            vehicle = rec['vehicle']
                            score = rec['score']
                            reasoning = rec['reasoning']
                            
                            with st.expander(f"Option #{i}: {vehicle.year} {vehicle.make} {vehicle.model} ({score:.0%} match)", expanded=False):
                                col_a, col_b = st.columns([3, 1])
                                
                                with col_a:
                                    st.write(f"**💰 Price:** ${vehicle.price:,}")
                                    st.write(f"**🚗 Mileage:** {vehicle.mileage:,} miles")
                                    if vehicle.mpg_city and vehicle.mpg_highway:
                                        st.write(f"**⛽ MPG:** {vehicle.mpg_city}/{vehicle.mpg_highway}")
                                    if vehicle.safety_rating:
                                        st.write(f"**🛡️ Safety:** {vehicle.safety_rating}/5 ⭐")
                                
                                with col_b:
                                    if score >= 0.8:
                                        st.success("🎯 Exceptional")
                                    elif score >= 0.6:
                                        st.info("✅ Great Match")
                                    else:
                                        st.warning("👍 Good Option")
                                
                                st.write(f"**Why I recommend this:** {reasoning}")
                    
                    # Additional options count
                    if len(recommendations) > 3:
                        st.markdown(f"#### 🚀 Plus {len(recommendations) - 3} More Options Available!")
                        st.write("I have additional carefully curated vehicles that might be perfect for you.")
                    
                    # Clear call to action
                    st.markdown("---")
                    st.markdown("### 💭 Questions About These Vehicles?")
                    col_x, col_y, col_z = st.columns(3)
                    with col_x:
                        st.write("• Compare features")
                        st.write("• Maintenance costs")
                    with col_y:
                        st.write("• Insurance estimates")  
                        st.write("• Financing options")
                    with col_z:
                        st.write("• Similar alternatives")
                        st.write("• Reliability data")
                    
                    response = ""  # No text response needed since we used Streamlit components
                    
                    # Show top 3 recommendations with detailed reasoning
                    for i, rec in enumerate(recommendations[:3], 1):
                        vehicle = rec['vehicle']
                        score = rec['score']
                        reasoning = rec['reasoning']
                        
                        # Dynamic intro based on ranking
                        if i == 1:
                            intro = "🏆 **My #1 Pick for You:**"
                        elif i == 2:
                            intro = "🥈 **Excellent Alternative:**"
                        else:
                            intro = "🥉 **Also Great:**"
                        
                        response += f"{intro} **{vehicle.year} {vehicle.make} {vehicle.model}**\n"
                        
                        # Price context
                        if preferences.get('budget_max'):
                            savings = preferences['budget_max'] - vehicle.price
                            if savings > 5000:
                                price_context = f"**${vehicle.price:,}** *(${savings:,} under budget - great value!)*"
                            elif savings > 0:
                                price_context = f"**${vehicle.price:,}** *(fits comfortably in budget)*"
                            else:
                                price_context = f"**${vehicle.price:,}**"
                        else:
                            price_context = f"**${vehicle.price:,}**"
                        
                        response += f"💰 **Price:** {price_context}\n"
                        
                        # Mileage with context
                        if vehicle.mileage < 15000:
                            mileage_context = f"{vehicle.mileage:,} miles *(practically new!)*"
                        elif vehicle.mileage < 30000:
                            mileage_context = f"{vehicle.mileage:,} miles *(low mileage)*"
                        else:
                            mileage_context = f"{vehicle.mileage:,} miles"
                        
                        response += f"🚗 **Mileage:** {mileage_context}\n"
                        
                        # Fuel efficiency with smart context
                        if vehicle.fuel_type == 'Electric':
                            response += f"⚡ **Powertrain:** Electric *(zero emissions, lowest operating costs)*\n"
                        elif vehicle.fuel_type == 'Hybrid':
                            if vehicle.mpg_city and vehicle.mpg_highway:
                                response += f"🌱 **Fuel Economy:** {vehicle.mpg_city}/{vehicle.mpg_highway} MPG *(hybrid efficiency saves $$$)*\n"
                            else:
                                response += f"🌱 **Powertrain:** Hybrid *(excellent fuel efficiency)*\n"
                        elif vehicle.mpg_city and vehicle.mpg_highway:
                            if vehicle.mpg_city > 30:
                                response += f"⛽ **Fuel Economy:** {vehicle.mpg_city}/{vehicle.mpg_highway} MPG *(great efficiency)*\n"
                            else:
                                response += f"⛽ **Fuel Economy:** {vehicle.mpg_city}/{vehicle.mpg_highway} MPG\n"
                        else:
                            response += f"⛽ **Fuel Type:** {vehicle.fuel_type}\n"
                        
                        # Safety with emphasis
                        if vehicle.safety_rating:
                            stars = '⭐' * int(vehicle.safety_rating)
                            if vehicle.safety_rating >= 5:
                                response += f"🛡️ **Safety:** {stars} *(top-rated safety - peace of mind)*\n"
                            elif vehicle.safety_rating >= 4:
                                response += f"🛡️ **Safety:** {stars} *(excellent safety ratings)*\n"
                            else:
                                response += f"🛡️ **Safety:** {stars}\n"
                        
                        # AI confidence score
                        if score >= 0.8:
                            confidence = "**Exceptional Match** 🎯"
                        elif score >= 0.6:
                            confidence = "**Strong Match** ✅"
                        else:
                            confidence = "**Good Match** 👍"
                        
                        response += f"🤖 **AI Confidence:** {score:.0%} - {confidence}\n"
                        
                        # Personalized reasoning
                        response += f"✨ **Why this is perfect for you:** {reasoning}\n"
                        
                        # Add vehicle description if available
                        if vehicle.description:
                            response += f"\n*{vehicle.description}*\n"
                        
                        response += "\n" + "─" * 50 + "\n\n"
                    
                    # Show additional options with personality
                    if len(recommendations) > 3:
                        response += f"🚀 **I've got {len(recommendations) - 3} more carefully selected options** that could be perfect for you! Want to see them, or should we dive deeper into any of these top picks?\n\n"
                    
                    # Engaging call to action
                    response += "� **Questions? Want details?** Ask me anything about these vehicles - maintenance costs, insurance estimates, feature comparisons, or how they'd fit your specific lifestyle!"
                    
                else:
                    response = "🤔 **Hmm, I'm having trouble finding the perfect match** for your specific requirements in our current inventory.\n\n"
                    response += "**Let me help you explore some options:**\n\n"
                    
                    # Provide intelligent suggestions based on what they asked for
                    if preferences.get('budget_max'):
                        # Check if there are vehicles slightly above budget
                        higher_budget_vehicles = car_ai.db_manager.search_vehicles(
                            max_price=preferences['budget_max'] * 1.2, limit=3
                        )
                        if higher_budget_vehicles:
                            response += f"💡 **Slightly above your ${preferences['budget_max']:,} budget:** I found some great options around ${higher_budget_vehicles[0].price:,} - would an extra ${higher_budget_vehicles[0].price - preferences['budget_max']:,} be worth it for the right car?\n\n"
                    
                    if preferences.get('make'):
                        # Suggest similar makes
                        similar_makes = {'toyota': ['honda', 'mazda'], 'honda': ['toyota', 'subaru'], 
                                       'bmw': ['audi', 'mercedes-benz'], 'ford': ['chevrolet']}
                        if preferences['make'].lower() in similar_makes:
                            suggestions = similar_makes[preferences['make'].lower()]
                            response += f"🔄 **Similar to {preferences['make']}:** Have you considered {', '.join(suggestions)}? They offer similar reliability and features.\n\n"
                    
                    response += "**Here's what I can do for you:**\n"
                    response += "• 📈 **Expand the search** - tell me what's flexible (budget, age, mileage?)\n"
                    response += "• 🎯 **Refine your needs** - what matters most? Reliability? Efficiency? Features?\n"
                    response += "• 📋 **Show alternatives** - similar vehicles that might surprise you\n"
                    response += "• 💬 **Just ask!** - 'Show me what's available under $25k' or 'What's the most reliable car you have?'\n\n"
                    response += "**I'm here to find you the perfect car - let's figure this out together!** 🤝"
                
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sidebar with current inventory stats (minimal, non-intrusive)
    with st.sidebar:
        st.markdown("### 📊 Current Inventory")
        
        # Get some quick stats
        all_vehicles = car_ai.db_manager.search_vehicles(limit=100)
        if all_vehicles:
            prices = [v.price for v in all_vehicles]
            
            st.metric("Total Vehicles", len(all_vehicles))
            st.metric("Price Range", f"${min(prices):,} - ${max(prices):,}")
            
            # Make distribution
            makes = {}
            for v in all_vehicles:
                makes[v.make] = makes.get(v.make, 0) + 1
            
            st.markdown("**Top Makes:**")
            for make, count in sorted(makes.items(), key=lambda x: x[1], reverse=True)[:5]:
                st.write(f"• {make}: {count}")

if __name__ == "__main__":
    main()