# CarFinder - GenAI Car Shopping Assistant

> ## ⚠️ **DISCLAIMER - INITIAL DEVELOPMENT PHASE**
> 
> **This is an early prototype using Ollama for local AI processing.** The system focuses on AI-powered conversational search rather than manual filtering. Simply chat with the AI about what vehicle you want and it will search live data sources to find matching vehicles.
> 
> **Current Capabilities:**
> - AI conversational search ("find me a reliable truck under $50k")
> - Live vehicle data from Auto.dev API (requires free account)
> - Location-based search with radius selection  
> - Truck class filtering (1500/2500/3500 specifications)
> - Natural language preference extraction
> 
> **Requirements:**
> - Auto.dev API key (free account at https://auto.dev/)
> - Ollama installation for local AI processing
> 
> **Known Limitations:**
> - Ollama LLM responses vary in quality and consistency
> - Limited to Auto.dev inventory (expanding to more sources)
> - AI may not capture highly nuanced or complex requirements

# 🚗 CarFinder - AI-Powered Car Shopping Assistant

An AI-powered car shopping assistant that lets you find vehicles through natural conversation. Just tell it what you're looking for and it searches live vehicle listings to find the perfect match.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.50+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Key Features

### 🤖 **Conversational AI Search**
- **Natural Language Interface**: "Find me a reliable truck under $50,000 with low mileage"
- **Smart Preference Extraction**: AI understands vehicle type, budget, mileage, location preferences
- **Truck Class Recognition**: Automatically detects 1500/2500/3500 specifications
- **Interactive Refinement**: Chat to clarify and adjust your requirements

### 🌐 **Live Vehicle Data**
- **Real-Time Search**: Searches current vehicle listings via Auto.dev API
- **Location-Based Results**: Find vehicles near you with customizable radius
- **Fresh Inventory**: Always up-to-date listings from dealers nationwide
- **Detailed Information**: Price, mileage, location, features, and dealer contact info

### 🎯 **AI-Powered Matching**
- **Compatibility Scoring**: AI rates how well each vehicle matches your needs
- **Missing Data Handling**: Smart penalties for incomplete listings
- **Vehicle Type Filtering**: Ensures trucks when you ask for trucks, not sedans
- **Transparent Results**: See why the AI recommended each vehicle

## How It Works

1. **Start a Conversation**: Type what kind of vehicle you're looking for
2. **AI Understands**: The system extracts your preferences (budget, type, location, etc.)
3. **Live Search**: Searches real-time vehicle listings from multiple sources
4. **Smart Filtering**: AI filters results and scores compatibility
5. **Get Results**: See matched vehicles with explanations of why they fit your needs

**Example Conversations:**
- "I need a reliable family SUV under $40k"
- "Find me a Ford F-250 with less than 50,000 miles near Seattle"
- "Looking for a fuel-efficient car for my commute, budget around $25k"

## Technology Stack

- **Frontend**: Streamlit with conversational interface
- **AI/LLM**: Ollama with Llama 3.1 (local, privacy-focused)
- **Live Data**: Auto.dev API for real-time vehicle listings
- **Conversation Agent**: Custom preference extraction and natural language processing
- **Vehicle Matching**: AI-powered compatibility scoring system
- **Database**: SQLite for local caching (optional)
- **Location Search**: Geographic radius-based filtering

## Quick Start

### Windows Setup
```bash
# 1. Clone the repository
git clone https://github.com/PatrickRay88/CarFinder.git
cd CarFinder

# 2. Run the automated setup
setup.bat

# 3. Get Auto.dev API key
# Visit https://auto.dev/ and sign up for free
# Copy your API key from the dashboard

# 4. Create .env file with your API key
echo AUTO_DEV_API_KEY=your_actual_api_key_here > .env

# 5. Install Ollama and models
# Download Ollama from https://ollama.ai
ollama pull llama3.1

# 6. Start the application
.\venv\Scripts\Activate.ps1
python -m streamlit run app/main_live.py
```

### Manual Setup (Any OS)
```bash
# 1. Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Get Auto.dev API key and create .env file
# Sign up at https://auto.dev/ for your free API key
echo "AUTO_DEV_API_KEY=your_actual_api_key_here" > .env

# 3. Install Ollama (https://ollama.ai)
ollama pull llama3.1

# 4. Run the app
streamlit run app/main_live.py
```

**That's it!** Open your browser to the provided URL and start chatting with the AI about what vehicle you want.

## Project Structure

```
CarFinder/
├── app/
│   ├── main_live.py            # Main Streamlit app with AI chat
│   ├── agents/
│   │   └── conversation.py     # AI conversation agent & preference extraction
│   ├── data_sources/
│   │   ├── auto_dev.py        # Auto.dev API integration
│   │   ├── aggregator.py      # Multi-source data aggregation
│   │   └── base.py           # Base data source interface
│   ├── services/
│   │   └── vehicle_data.py    # Vehicle search & filtering logic
│   ├── ui/
│   │   ├── components.py      # Chat interface & vehicle cards
│   │   ├── sidebar.py         # Location & preference inputs
│   │   └── results.py         # Search results display
│   └── utils/
│       ├── config.py          # Configuration management
│       └── validators.py      # Input validation
├── data/
│   └── sample_listings.csv    # Sample data for fallback
├── scripts/
│   ├── setup_database.py      # Initialize local database
│   └── ingest_sample_data.py  # Load sample data
├── setup.bat                  # Windows automated setup
├── requirements.txt           # Python dependencies
└── README.md                  # This file
├── pytest.ini                 # Test configuration
└── README.md                   # This file
```

## Usage

### AI Chat Interface (Recommended)
1. **Start Chatting**: Type your vehicle needs in the chat box
   - "I need a reliable pickup truck under $45,000"
   - "Find me a Honda Civic with less than 30k miles near Chicago"
   - "Looking for a family SUV, budget around $35k, good safety ratings"

2. **AI Processing**: The system automatically:
   - Extracts your preferences (vehicle type, budget, location, etc.)
   - Searches live vehicle listings
   - Filters and scores results for compatibility

3. **Get Results**: View matched vehicles with:
   - AI compatibility scores and explanations
   - Vehicle details (price, mileage, location, features)
   - Dealer contact information
   - Why each vehicle was recommended

### Manual Search (Alternative)
1. **Set Preferences**: Use the sidebar for manual input
   - Budget range and location
   - Vehicle type and specific requirements
   - Search radius and other filters

2. **Search**: Click "Search Vehicles" to find matches
3. **Review Results**: Browse AI-scored and filtered results

### Tips for Best Results
- **Be Specific**: "Ford F-150 under $40k" works better than just "truck"
- **Include Location**: "near Seattle" or "within 50 miles of 98101"
- **Mention Priorities**: "reliable", "fuel efficient", "low mileage", etc.
- **Ask Follow-ups**: Refine your search with additional requirements

## Configuration

### Required Setup

1. **Ollama Installation**: Download from https://ollama.ai
2. **AI Model**: Run `ollama pull llama3.1` to download the language model
3. **Auto.dev API Key**: 
   - Sign up at https://auto.dev/ for free account
   - Get your API key from the dashboard
   - Add it to your `.env` file (see below)

### Configuration

Create a `.env` file in the project root:
```bash
# Required: Auto.dev API for live vehicle data
AUTO_DEV_API_KEY=your_auto_dev_api_key_here

# Optional: Ollama Configuration (defaults work for most setups)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Optional: Search Limits
MAX_RESULTS=20
DEFAULT_RADIUS=100  # miles
```

**⚠️ Important**: Never commit your `.env` file with real API keys to Git!

### Performance Notes
- **Ollama Models**: `llama3.1` (8B) works well for most systems
- **For Better Performance**: Use `llama3.1:70b` if you have 32GB+ RAM
- **For Lower Resources**: Try `llama3.2` (3B) for faster responses

## Troubleshooting

### Common Issues

**"Ollama connection failed"**
- Install Ollama: Download from https://ollama.ai
- Start Ollama: It should start automatically, or run `ollama serve`
- Pull model: `ollama pull llama3.1`

**"API Authentication Failed" or "No vehicles found"**
- Ensure you have a valid Auto.dev API key in your `.env` file
- Check that your API key is correctly formatted (no extra spaces)
- Verify your Auto.dev account is active at https://auto.dev/
- Try a broader location or larger radius
- Ensure internet connection (needs to access Auto.dev API)

**"App won't start"**
- Activate virtual environment: `.\venv\Scripts\Activate.ps1` (Windows)
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: Requires Python 3.8+

**Performance Issues**
- For faster responses: Use `ollama pull llama3.2` (smaller model)
- For better quality: Use `ollama pull llama3.1:70b` (if you have 32GB+ RAM)
- Close other applications to free up system resources

### Getting Help
- Check the conversation logs in the Streamlit interface
- Try rephrasing your vehicle search request
- Use more specific terms ("Ford F-150" vs "pickup truck")

## Privacy & Security

- **Local AI**: All AI processing happens on your computer via Ollama
- **No Personal Data Stored**: Your conversations aren't permanently saved
- **Live Data**: Vehicle listings come from Auto.dev API (public data)
- **Open Source**: Full source code available for inspection

## License

MIT License - see LICENSE file for details.

## Future Enhancements

- **Additional Data Sources**: Integration with Cars.com, AutoTrader, CarGurus
- **Enhanced AI**: More sophisticated conversation and preference understanding
- **Mobile App**: Native mobile application
- **Dealer Integration**: Direct contact and test drive scheduling
- **Price Alerts**: Notifications when matching vehicles become available