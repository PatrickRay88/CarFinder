# CarFinder - GenAI Car Shopping Assistant

A complete Streamlit-based AI car shopping assistant with RAG-powered search, multi-objective recommendations, and conversational AI agent.

## Architecture & Technology Stack

- **Frontend**: Streamlit with responsive sidebar and results display
- **Backend**: SQLite database with SQLAlchemy ORM
- **AI/ML**: Sentence Transformers + FAISS for semantic search, Ollama (Llama 3.1) for conversations  
- **Agent Framework**: Custom conversational agent with preference extraction
- **Vector Search**: FAISS index with normalized embeddings for vehicle similarity

## Quick Start Commands

```bash
# Windows setup (run once)
setup.bat

# Or manual setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts/setup_database.py
python scripts/ingest_sample_data.py

# Install Ollama models
ollama pull llama3.1
ollama pull nomic-embed-text

# Run application
streamlit run app/main.py
```

## Key Development Patterns

### Database Operations (`app/models/database.py`)
- `Vehicle` model with JSON features storage and embedding blob
- `DatabaseManager` singleton with search filters and stats
- SQLite WAL mode enabled for concurrent access
- Validation in `app/utils/validators.py` for all inputs

### RAG Pipeline (`app/rag/retriever.py`)
- `VehicleRetriever` combines database filters + semantic search
- FAISS index auto-created from vehicle descriptions
- Embeddings cached and persisted in `data/faiss_index.pkl`
- Similarity threshold filtering (default 0.7)

### Recommendation Engine (`app/recommendations/engine.py`)
- Multi-objective scoring: price, reliability, fuel efficiency, safety, features
- User preference weights from sidebar sliders
- Explanation generation for transparency
- Make-specific reliability scores built-in

### Conversational Agent (`app/agents/conversation.py`)
- `ConversationState` tracks preferences and history
- Ollama integration with fallback rule-based responses
- Preference extraction from natural language
- Context-aware response generation

### UI Components (`app/ui/`)
- `sidebar.py`: All preference inputs with validation
- `results.py`: Search results with sorting and comparison
- `components.py`: Reusable vehicle cards and chat interface
- Session state management for preferences and chat history

## Data Flow Architecture

1. **Preference Input**: Sidebar collects structured preferences (budget, make, features, etc.)
2. **Optional Chat**: Conversational agent can clarify ambiguous needs  
3. **Hybrid Search**: Database filters + semantic vector search via FAISS
4. **Scoring**: Multi-objective recommendation engine ranks results
5. **Display**: Results shown as curated list + top pick with explanations

## Configuration & Environment

### Required Environment Variables (.env)
- `OLLAMA_HOST`: Local Ollama server (default: http://localhost:11434)
- `OLLAMA_MODEL`: LLM model name (default: llama3.1)  
- `EMBEDDING_MODEL`: Embedding model (default: nomic-embed-text)
- `DATABASE_PATH`: SQLite database location (default: data/carfinder.db)

### Performance Settings
- `MAX_RESULTS`: Limit search results (default: 20)
- `SIMILARITY_THRESHOLD`: Minimum embedding similarity (default: 0.7)
- `RERANK_TOP_K`: Results to rerank (default: 10)

## Development Workflows

### Adding New Vehicle Data
1. Add CSV to `data/` directory with required columns
2. Run `python scripts/ingest_sample_data.py --file your_data.csv`
3. Update search index: `python scripts/update_embeddings.py`

### Testing Search & Recommendations
```python
from app.rag.retriever import VehicleRetriever
from app.recommendations.engine import RecommendationEngine

config = load_config()
retriever = VehicleRetriever(config)
engine = RecommendationEngine(config)

# Test search
preferences = {'budget_max': 30000, 'fuel_type': 'Hybrid'}
results = retriever.search(preferences)
recommendations = engine.recommend(results, preferences)
```

### Database Schema Key Points
- `Vehicle.embedding`: Binary blob for FAISS vector storage
- `Vehicle.features`: JSON string array of feature names
- `Vehicle.vin`: Unique identifier for recall checks
- Indexed fields: make, model, year, price, mileage, fuel_type

## AI Model Integration

### Ollama Local Setup
- Models stored locally for privacy
- Fallback responses if Ollama unavailable
- Chat history maintained in session state
- Preference extraction via regex + LLM parsing

### Embedding Strategy
- Vehicle descriptions generated from: make/model/year + features + description
- Sentence Transformers with cosine similarity
- Normalized embeddings stored in FAISS IndexFlatIP
- Incremental index updates for new vehicles

## Security & Privacy Implementation

- **Input Validation**: All user inputs sanitized via `validators.py`
- **No PII Storage**: Only vehicle data and anonymous preferences
- **Local Processing**: Ollama runs locally, no cloud API calls required
- **Environment Security**: Sensitive config in `.env` (gitignored)

## Troubleshooting Common Issues

### Ollama Connection Issues
- Verify Ollama running: `ollama list`
- Check host/port in .env file
- Fallback responses work without Ollama

### Database/Search Issues  
- Reset database: Delete `data/carfinder.db` and re-run setup
- Rebuild index: `python scripts/update_embeddings.py`
- Check file permissions in data/ directory

### Import Errors
- Activate virtual environment: `venv\Scripts\activate`
- Install missing packages: `pip install -r requirements.txt`
- Verify Python 3.8+ version