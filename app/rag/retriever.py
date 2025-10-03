"""Vehicle retriever with RAG capabilities."""
import numpy as np
from typing import List, Dict, Any, Optional
import pickle
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from app.models.database import get_database_manager, Vehicle
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from models.database import get_database_manager, Vehicle

class VehicleRetriever:
    """RAG-based vehicle retriever with semantic search."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = get_database_manager()
        self.embedding_model = None
        self.faiss_index = None
        self.vehicle_ids = []
        
        # Initialize embedding model
        self._load_embedding_model()
        self._load_or_create_index()
    
    def _load_embedding_model(self):
        """Load the sentence transformer model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("Warning: sentence-transformers not available, semantic search disabled")
            self.embedding_model = None
            return
            
        model_name = self.config.get('embedding_model', 'all-MiniLM-L6-v2')
        try:
            # Try to load with explicit device and trust_remote_code settings
            import torch
            device = 'cpu'  # Force CPU to avoid GPU compatibility issues
            self.embedding_model = SentenceTransformer(
                model_name, 
                device=device,
                trust_remote_code=True
            )
        except Exception as e:
            print(f"Failed to load {model_name}: {e}")
            try:
                # Try a different approach with explicit CPU device
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            except Exception as e2:
                print(f"Failed to load fallback model: {e2}")
                # Disable embedding model if all loading attempts fail
                self.embedding_model = None
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create new one."""
        index_path = Path(self.config['data_dir']) / 'faiss_index.pkl'
        ids_path = Path(self.config['data_dir']) / 'vehicle_ids.pkl'
        
        if index_path.exists() and ids_path.exists():
            try:
                with open(index_path, 'rb') as f:
                    self.faiss_index = pickle.load(f)
                with open(ids_path, 'rb') as f:
                    self.vehicle_ids = pickle.load(f)
                return
            except Exception:
                pass
        
        # Create new index
        self._create_new_index()
    
    def _create_new_index(self):
        """Create new FAISS index from database vehicles."""
        if not self.embedding_model:
            # No embedding model available, skip index creation
            self.faiss_index = None
            self.vehicle_ids = []
            return
            
        vehicles = self.db_manager.get_all_vehicles()
        
        if not vehicles:
            # Create empty index
            if FAISS_AVAILABLE:
                self.faiss_index = faiss.IndexFlatIP(384)  # Default embedding dimension
            else:
                self.faiss_index = None
            self.vehicle_ids = []
            return
        
        # Generate embeddings for all vehicles
        descriptions = []
        vehicle_ids = []
        
        for vehicle in vehicles:
            description = self._create_vehicle_description(vehicle)
            descriptions.append(description)
            vehicle_ids.append(vehicle.id)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(descriptions)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings.astype(np.float32))
        self.faiss_index.add(embeddings.astype(np.float32))
        
        self.vehicle_ids = vehicle_ids
        
        # Save index
        self._save_index()
    
    def _create_vehicle_description(self, vehicle: Vehicle) -> str:
        """Create searchable description for vehicle."""
        parts = [
            f"{vehicle.year} {vehicle.make} {vehicle.model}"
        ]
        
        if vehicle.fuel_type:
            parts.append(f"fuel type {vehicle.fuel_type}")
        
        if vehicle.transmission:
            parts.append(f"transmission {vehicle.transmission}")
        
        if vehicle.features:
            import json
            try:
                features = json.loads(vehicle.features) if isinstance(vehicle.features, str) else vehicle.features
                if features:
                    parts.append(f"features {' '.join(features)}")
            except (json.JSONDecodeError, TypeError):
                pass
        
        if vehicle.description:
            parts.append(vehicle.description)
        
        if vehicle.mpg_city and vehicle.mpg_highway:
            parts.append(f"fuel efficiency {vehicle.mpg_city} city {vehicle.mpg_highway} highway mpg")
        
        return " ".join(parts).lower()
    
    def _save_index(self):
        """Save FAISS index and vehicle IDs."""
        index_path = Path(self.config['data_dir']) / 'faiss_index.pkl'
        ids_path = Path(self.config['data_dir']) / 'vehicle_ids.pkl'
        
        try:
            with open(index_path, 'wb') as f:
                pickle.dump(self.faiss_index, f)
            with open(ids_path, 'wb') as f:
                pickle.dump(self.vehicle_ids, f)
        except Exception as e:
            print(f"Warning: Could not save FAISS index: {e}")
    
    def search(self, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search vehicles based on user preferences."""
        # First, apply database filters
        db_results = self._search_database(preferences)
        
        # If we have semantic search query, use RAG
        if preferences.get('query') or preferences.get('description'):
            semantic_results = self._semantic_search(preferences)
            # Combine and deduplicate results
            combined_results = self._combine_results(db_results, semantic_results)
            return combined_results
        
        # Convert to standard format
        return [{'vehicle': vehicle.to_dict(), 'score': 1.0} for vehicle in db_results]
    
    def _search_database(self, preferences: Dict[str, Any]) -> List[Vehicle]:
        """Search database with structured filters."""
        return self.db_manager.search_vehicles(
            make=preferences.get('make'),
            min_year=preferences.get('min_year'),
            max_year=preferences.get('max_year'),
            min_price=preferences.get('budget_min'),
            max_price=preferences.get('budget_max'),
            fuel_type=preferences.get('fuel_type'),
            min_mpg=preferences.get('min_mpg'),
            max_mileage=preferences.get('max_mileage'),
            limit=self.config.get('max_results', 20)
        )
    
    def _semantic_search(self, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform semantic search using FAISS."""
        if not self.faiss_index or not self.vehicle_ids or not self.embedding_model:
            return []
        
        # Create search query
        query_parts = []
        
        if preferences.get('query'):
            query_parts.append(preferences['query'])
        
        if preferences.get('description'):
            query_parts.append(preferences['description'])
        
        # Add preference-based query enhancement
        if preferences.get('make'):
            query_parts.append(preferences['make'])
        
        if preferences.get('fuel_type'):
            query_parts.append(preferences['fuel_type'])
        
        if preferences.get('desired_features'):
            query_parts.extend(preferences['desired_features'])
        
        if not query_parts:
            return []
        
        query = " ".join(query_parts).lower()
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding.astype(np.float32))
        
        # Search
        k = min(self.config.get('max_results', 20), len(self.vehicle_ids))
        similarities, indices = self.faiss_index.search(query_embedding.astype(np.float32), k)
        
        # Get vehicles and scores
        results = []
        threshold = self.config.get('similarity_threshold', 0.7)
        
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if similarity >= threshold and idx < len(self.vehicle_ids):
                vehicle_id = self.vehicle_ids[idx]
                vehicle = self.db_manager.get_vehicle_by_id(vehicle_id)
                
                if vehicle:
                    results.append({
                        'vehicle': vehicle.to_dict(),
                        'score': float(similarity),
                        'rank': i + 1
                    })
        
        return results
    
    def _combine_results(self, db_results: List[Vehicle], semantic_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine database and semantic search results."""
        # Convert db results to dict format
        db_dict = {vehicle.id: {'vehicle': vehicle.to_dict(), 'score': 1.0} for vehicle in db_results}
        
        # Merge with semantic results (semantic scores take priority)
        for result in semantic_results:
            vehicle_id = result['vehicle']['id']
            if vehicle_id in db_dict:
                # Boost score for vehicles that match both filters and semantic search
                result['score'] = min(1.0, result['score'] + 0.1)
            db_dict[vehicle_id] = result
        
        # Sort by score and return
        combined = list(db_dict.values())
        combined.sort(key=lambda x: x['score'], reverse=True)
        
        return combined[:self.config.get('max_results', 20)]
    
    def update_index(self):
        """Rebuild the FAISS index with latest data."""
        self._create_new_index()
    
    def add_vehicle_to_index(self, vehicle: Vehicle):
        """Add a single vehicle to the existing index."""
        if not self.faiss_index:
            self._create_new_index()
            return
        
        description = self._create_vehicle_description(vehicle)
        embedding = self.embedding_model.encode([description])
        faiss.normalize_L2(embedding.astype(np.float32))
        
        self.faiss_index.add(embedding.astype(np.float32))
        self.vehicle_ids.append(vehicle.id)
        
        self._save_index()