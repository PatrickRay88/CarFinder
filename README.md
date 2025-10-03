# CarFinder - GenAI Car Shopping Assistant

# 🚗 CarFinder - AI-Powered Car Shopping Assistant

A complete GenAI car shopping assistant built with Streamlit, featuring RAG-powered search, intelligent recommendations, and conversational AI interface.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.50+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🤖 **AI-First Experience**
- **Natural Language Search**: Describe what you want instead of filling forms
- **Conversational Interface**: Chat with AI to refine and explore options
- **Contextual Understanding**: AI extracts preferences from casual conversation

### 🎯 **Intelligent Recommendations**
- **RAG-Powered Search**: Semantic vehicle matching using custom RAG implementation
- **Multi-Objective Scoring**: Considers price, reliability, fuel efficiency, safety, and features
- **Personalized Ranking**: AI learns from your preferences and priorities

### 🎨 **Beautiful Interface**
- **Card-Based Layout**: Clean, modern vehicle display cards
- **Prominent Top Choice**: AI's #1 recommendation gets prime visual real estate
- **Smart Metrics**: Context-aware data presentation with savings indicators

### 🔧 **Robust Architecture**
- **Fallback-Friendly**: Graceful degradation when advanced features unavailable
- **Local Processing**: No external API dependencies for core functionality
- **SQLite Database**: Lightweight, embedded database with sample vehicle data

## Features

- **Conversational AI**: Chat with an AI agent about your car needs and preferences
- **Smart Search**: RAG-powered semantic search through vehicle listings
- **Personalized Recommendations**: Get a curated shortlist and optimized best pick
- **Intelligent Agent**: Optional clarification agent to refine your preferences
- **Safety Focus**: VIN-based recall checks and safety ratings
- **Cost Analysis**: Total Cost of Ownership (TCO) estimation
- **Local Privacy**: All AI processing runs locally via Ollama

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI (optional)
- **Database**: SQLite with full-text search
- **Vector Search**: FAISS/Chroma for semantic similarity
- **Embeddings**: Sentence Transformers (MiniLM/BGE)
- **LLM**: Llama 3.1 via Ollama (local, privacy-focused)
- **Agent Framework**: LangGraph for conversational flows

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone https://github.com/PatrickRay88/CarFinder.git
   cd CarFinder
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install Ollama and Models**
   ```bash
   # Install Ollama (see https://ollama.ai)
   ollama pull llama3.1
   ollama pull nomic-embed-text  # For embeddings
   ```

3. **Initialize Database**
   ```bash
   python scripts/setup_database.py
   python scripts/ingest_sample_data.py
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the Application**
   ```bash
   streamlit run app/main.py
   ```

## Project Structure

```
CarFinder/
├── app/
│   ├── main.py                 # Streamlit entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── vehicle.py          # Vehicle data models
│   │   └── database.py         # Database operations
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py       # Text embedding utilities
│   │   ├── retriever.py        # Vector search and retrieval
│   │   └── reranker.py         # Optional result reranking
│   ├── recommendations/
│   │   ├── __init__.py
│   │   ├── engine.py           # Recommendation logic
│   │   └── scoring.py          # Multi-objective scoring
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── conversation.py     # LangGraph conversation flow
│   │   ├── search_agent.py     # Search orchestration
│   │   └── clarifier.py        # Preference clarification
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── components.py       # Reusable UI components
│   │   ├── sidebar.py          # Preference input sidebar
│   │   └── results.py          # Results display
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       ├── ollama_client.py    # Ollama integration
│       └── validators.py       # Input validation
├── data/
│   ├── sample_listings.csv     # Sample vehicle data
│   ├── safety_ratings.json     # NHTSA safety data
│   └── recalls.json            # Recall information
├── scripts/
│   ├── setup_database.py       # Database initialization
│   ├── ingest_data.py          # Data ingestion pipeline
│   └── update_embeddings.py    # Rebuild vector index
├── tests/
│   ├── __init__.py
│   ├── test_rag.py
│   ├── test_recommendations.py
│   └── test_agents.py
├── config/
│   ├── __init__.py
│   └── settings.py             # Application settings
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── pytest.ini                 # Test configuration
└── README.md                   # This file
```

## Usage

### Basic Car Search
1. Open the Streamlit app
2. Use the sidebar to set your preferences (budget, make, fuel type, etc.)
3. View your curated shortlist and optimized best pick
4. Explore detailed vehicle information and recommendations

### Conversational Agent Mode
1. Click "Chat with AI Agent" 
2. Describe your needs in natural language
3. The agent will ask clarifying questions to refine your search
4. Get personalized recommendations with detailed explanations

### Advanced Features
- **VIN Lookup**: Check for recalls and detailed vehicle history
- **TCO Calculator**: Compare total ownership costs over time
- **Dealer Proximity**: Find nearby dealers for test drives
- **Comparison Tool**: Side-by-side vehicle comparisons

## Configuration

### Environment Variables (.env)
```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1
EMBEDDING_MODEL=nomic-embed-text

# Database
DATABASE_PATH=data/carfinder.db

# Search Configuration
MAX_RESULTS=20
SIMILARITY_THRESHOLD=0.7

# Optional: External APIs
NHTSA_API_KEY=your_key_here
RECALLS_API_ENDPOINT=https://api.nhtsa.gov/recalls
```

### Model Selection Guide
- **Embeddings**: `nomic-embed-text` (recommended) or `sentence-transformers/all-MiniLM-L6-v2`
- **LLM**: `llama3.1` (8B parameter, good balance) or `llama3.1:70b` (better quality, requires more resources)
- **Reranker**: `ms-marco-MiniLM-L-6-v2` for improved search relevance

## Development

### Adding New Vehicle Data
1. Place CSV files in `data/` directory
2. Run `python scripts/ingest_data.py --file your_data.csv`
3. Update embeddings: `python scripts/update_embeddings.py`

### Testing
```bash
pytest tests/ -v
pytest tests/test_rag.py -k "test_semantic_search"
```

### Database Schema
```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER,
    price REAL,
    mileage INTEGER,
    fuel_type TEXT,
    transmission TEXT,
    location TEXT,
    features TEXT,  -- JSON array
    safety_rating REAL,
    mpg_city INTEGER,
    mpg_highway INTEGER,
    vin TEXT UNIQUE,
    description TEXT,
    embedding BLOB,  -- Vector embedding
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Security & Privacy

- **Local-First**: All AI processing via local Ollama installation
- **No PII Storage**: Vehicle preferences not permanently stored
- **Input Sanitization**: All user inputs validated and sanitized
- **Environment Security**: Sensitive configuration in `.env` (not committed)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Troubleshooting

### Common Issues
- **Ollama Connection**: Ensure Ollama is running (`ollama serve`)
- **Model Not Found**: Pull required models (`ollama pull llama3.1`)
- **Database Locked**: Close other connections to SQLite database
- **Memory Issues**: Use smaller models or increase system resources

### Performance Tips
- Use FAISS for large datasets (>10k vehicles)
- Enable SQLite WAL mode for concurrent access
- Cache embeddings to avoid recomputation
- Use GPU acceleration with Ollama if available