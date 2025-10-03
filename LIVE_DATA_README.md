# 🚗 CarFinder AI - Real-Time Vehicle Data Integration

## New Features in v2.0 (Live Data Branch)

### 🌐 Multi-Source Vehicle Data
- **Live Market Integration**: Real-time vehicle listings from Cars.com, AutoTrader, and CarGurus
- **Hybrid Search**: Combines local database with live market data
- **Smart Deduplication**: Removes duplicate listings across sources
- **Intelligent Ranking**: AI-powered result ranking based on user preferences

### 🔍 Enhanced Search Capabilities
- **Concurrent API Calls**: Searches multiple sources simultaneously 
- **Adaptive Filtering**: Matches preferences across different data formats
- **Source Reliability Scoring**: Weighs results based on data source quality
- **Live Data Toggle**: Users can choose between local-only or live+local searches

### 📊 Data Source Management
- **Source Status Dashboard**: View active data sources and statistics
- **Automatic Caching**: Stores live results locally to improve performance
- **API Health Monitoring**: Tracks data source availability and response times
- **Rate Limiting**: Respects API limits and website terms of service

## Quick Start - Live Data Branch

```bash
# Switch to the live data feature branch
git checkout vehicle-data-api

# Install additional dependencies
pip install -r requirements.txt

# Configure API keys (optional - works with mock data)
cp .env.vehicle_apis .env_vehicle_apis
# Edit .env_vehicle_apis with your API keys

# Run the enhanced application
streamlit run app/main_live.py
```

## Data Source Configuration

### Supported Sources

1. **Cars.com** 🆓
   - Method: Web scraping (respectful)
   - Cost: Free
   - Coverage: National
   - Status: Mock implementation (demo)

2. **AutoTrader** 🔑
   - Method: Official API
   - Cost: Requires subscription
   - Coverage: National + Canada
   - Status: Mock implementation ready for API integration

3. **CarGurus** 🔑  
   - Method: Official API
   - Cost: Requires partnership
   - Coverage: National
   - Status: Mock implementation ready for API integration

### API Configuration

Create `.env_vehicle_apis` file:

```env
# AutoTrader API (requires subscription)
AUTOTRADER_API_KEY=your_api_key_here
AUTOTRADER_BASE_URL=https://api.autotrader.com/v1

# CarGurus API (requires partnership)  
CARGURUS_API_KEY=your_api_key_here
CARGURUS_BASE_URL=https://api.cargurus.com/v1

# Performance Settings
ENABLE_LIVE_DATA=true
CACHE_DURATION_HOURS=2
MAX_RESULTS_PER_SOURCE=10
DEFAULT_SEARCH_RADIUS=50
```

## Architecture Overview

### Data Flow
```
User Query → AI Preference Extraction → Hybrid Search Engine
                                      ↓
Local Database ← Data Aggregator → Live Sources (Cars.com, AutoTrader, CarGurus)
                                      ↓
              Deduplication & Ranking → AI-Scored Results → User Interface
```

### New Components

#### `app/data_sources/`
- `base.py`: Abstract base class for all data sources
- `cars_com.py`: Cars.com integration (web scraping)
- `autotrader.py`: AutoTrader API integration
- `cargurus.py`: CarGurus API integration  
- `aggregator.py`: Multi-source data coordinator

#### `app/services/`
- `vehicle_data.py`: Hybrid search service combining local + live data

#### `app/main_live.py`
- Enhanced UI with live data controls
- Real-time source status dashboard
- Improved vehicle cards with source attribution

## Usage Examples

### Natural Language Queries with Live Data
```
"Find me a reliable Toyota under $30k with low mileage"
→ Searches local DB + Cars.com + AutoTrader + CarGurus
→ Returns ranked results with source attribution

"I need a fuel-efficient car for commuting, budget around $25k"  
→ AI extracts preferences: fuel_type=hybrid/electric, budget_max=25000
→ Searches all sources with intelligent filtering
```

### Programmatic Access
```python
from app.services.vehicle_data import VehicleDataService
from app.data_sources.aggregator import SearchCriteria

service = VehicleDataService()

# Hybrid search (local + live)
results = service.search_vehicles_hybrid({
    'make': 'Toyota',
    'budget_max': 30000,
    'fuel_type': 'Hybrid'
}, use_live_data=True)

# Live-only search
criteria = SearchCriteria(make='Honda', price_max=25000)
live_results = service.aggregator.search_all_sources(criteria)
```

## Performance & Reliability

### Caching Strategy
- **Smart Caching**: Live results cached locally for 2 hours
- **Incremental Updates**: New data merged with existing cache
- **Cache Invalidation**: Automatic refresh based on search patterns

### Error Handling
- **Graceful Fallbacks**: Falls back to local data if live sources fail
- **Source-Level Resilience**: Individual source failures don't break search
- **User Notifications**: Clear indicators of data source status

### Rate Limiting
- **Respectful Scraping**: Built-in delays for web scraping
- **API Quota Management**: Tracks and respects API limits
- **Concurrent Request Limits**: Prevents overwhelming data sources

## Real-World Integration Notes

### Production Considerations

1. **API Costs**: Most vehicle data APIs require paid subscriptions
2. **Legal Compliance**: Web scraping must respect robots.txt and ToS
3. **Data Quality**: Live data requires validation and normalization
4. **Update Frequency**: Balance freshness with API costs

### Current Implementation Status

- ✅ **Architecture**: Complete multi-source framework
- ✅ **Mock Data**: Realistic demo data for all sources
- ✅ **UI Integration**: Full user interface with live data controls
- ⚠️ **API Integration**: Ready for real API keys (currently mock)
- ⚠️ **Web Scraping**: Demo implementation (needs production hardening)

## Development Roadmap

### Phase 1: Foundation ✅
- [x] Multi-source architecture
- [x] Data aggregation and deduplication
- [x] UI integration with live data toggle
- [x] Mock implementations for all sources

### Phase 2: Production APIs 🔄
- [ ] Real AutoTrader API integration
- [ ] Real CarGurus API integration  
- [ ] Production-grade error handling
- [ ] Comprehensive testing

### Phase 3: Advanced Features 📋
- [ ] Machine learning for result ranking
- [ ] Price prediction and market analysis
- [ ] Advanced filtering (dealer ratings, vehicle history)
- [ ] Mobile app development

## Testing the Live Data Feature

### Demo Mode (No API Keys Required)
```bash
# Run with mock data
streamlit run app/main_live.py

# Toggle "Live Data" in the UI to see multi-source results
# Ask: "Find me a Tesla under $40k"
# See results from multiple mock sources
```

### With Real APIs (When Available)
```bash
# Add your API keys to .env_vehicle_apis
AUTOTRADER_API_KEY=your_real_key
CARGURUS_API_KEY=your_real_key

# Run the application
streamlit run app/main_live.py
```

## Monitoring & Analytics

### Data Source Dashboard
- Real-time status of all data sources
- API response times and success rates
- Cache hit/miss ratios
- Search result quality metrics

### User Experience Metrics  
- Average search result relevance scores
- User interaction patterns with live vs local data
- Performance impact of multi-source searches
- Error rates and fallback usage

---

This live data integration represents a major advancement in CarFinder's capabilities, providing users with access to real-time market data while maintaining the intelligent AI-powered search experience.