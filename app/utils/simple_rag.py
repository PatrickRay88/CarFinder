"""
Simple but effective RAG implementation for vehicle recommendations
Uses keyword matching, semantic similarity, and contextual understanding
"""
import re
from typing import List, Dict, Any
from collections import Counter
import math

class SimpleRAG:
    """Simple but effective RAG implementation for vehicle search."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.vehicle_corpus = self._build_corpus()
    
    def _build_corpus(self) -> Dict[int, str]:
        """Build searchable text corpus for all vehicles."""
        corpus = {}
        vehicles = self.db_manager.search_vehicles(limit=100)
        
        for vehicle in vehicles:
            # Create comprehensive text representation
            text_parts = [
                f"{vehicle.make} {vehicle.model}",
                f"{vehicle.year} model",
                vehicle.fuel_type or "",
                vehicle.description or "",
            ]
            
            # Add feature keywords
            if vehicle.features:
                try:
                    import json
                    features = json.loads(vehicle.features) if isinstance(vehicle.features, str) else vehicle.features
                    text_parts.extend(features)
                except:
                    pass
            
            # Add contextual keywords based on vehicle characteristics
            context_keywords = []
            
            # Budget category
            if vehicle.price < 25000:
                context_keywords.extend(["budget", "affordable", "economical"])
            elif vehicle.price > 40000:
                context_keywords.extend(["luxury", "premium", "high-end"])
            else:
                context_keywords.extend(["mid-range", "value"])
            
            # Vehicle type keywords
            if vehicle.make.lower() == 'tesla' or vehicle.fuel_type == 'Electric':
                context_keywords.extend(["electric", "ev", "sustainable", "tech"])
            
            if vehicle.fuel_type == 'Hybrid':
                context_keywords.extend(["eco", "green", "efficient"])
            
            # Size/type inference from model name
            model_lower = vehicle.model.lower()
            if any(x in model_lower for x in ['suv', 'cr-v', 'cx-5', 'escape', 'equinox']):
                context_keywords.extend(["suv", "family", "spacious", "utility"])
            elif any(x in model_lower for x in ['civic', 'camry', 'accord', 'altima']):
                context_keywords.extend(["sedan", "reliable", "practical"])
            elif any(x in model_lower for x in ['f-150', 'truck']):
                context_keywords.extend(["truck", "work", "hauling", "capability"])
            
            # Reliability keywords for known reliable brands
            if vehicle.make.lower() in ['toyota', 'honda']:
                context_keywords.extend(["reliable", "dependable", "long-lasting"])
            
            # Age keywords
            if vehicle.year >= 2023:
                context_keywords.extend(["new", "latest", "modern"])
            elif vehicle.year >= 2020:
                context_keywords.extend(["recent", "current"])
            
            # Mileage keywords
            if vehicle.mileage < 20000:
                context_keywords.extend(["low-mileage", "like-new"])
            
            text_parts.extend(context_keywords)
            corpus[vehicle.id] = " ".join(text_parts).lower()
        
        return corpus
    
    def semantic_search(self, query: str, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform semantic search using keyword matching and contextual understanding."""
        query_lower = query.lower()
        
        # Extract key terms from query
        query_terms = self._extract_key_terms(query_lower)
        
        # Score each vehicle
        scored_vehicles = []
        
        for vehicle_id, vehicle_text in self.vehicle_corpus.items():
            score = self._calculate_text_similarity(query_terms, vehicle_text, preferences)
            
            if score > 0.1:  # Minimum relevance threshold
                vehicle = self.db_manager.get_vehicle_by_id(vehicle_id)
                if vehicle:
                    scored_vehicles.append({
                        'vehicle': vehicle,
                        'score': score,
                        'relevance': self._explain_relevance(query_terms, vehicle_text, vehicle)
                    })
        
        # Sort by score
        scored_vehicles.sort(key=lambda x: x['score'], reverse=True)
        return scored_vehicles[:10]
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract meaningful terms from user query."""
        # Remove common stop words
        stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
                     'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
                     'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                     'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                     'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                     'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                     'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
                     'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
                     'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                     'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                     'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
                     'just', 'don', 'should', 'now', 'want', 'need', 'looking', 'find', 'get', 'car', 'vehicle'}
        
        # Extract words and important phrases
        words = re.findall(r'\b\w+\b', query)
        filtered_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add important multi-word phrases
        phrases = [
            'fuel efficient', 'gas mileage', 'low maintenance', 'family car',
            'sports car', 'work truck', 'city driving', 'highway driving',
            'all wheel drive', 'four wheel drive', 'manual transmission',
            'automatic transmission', 'backup camera', 'navigation system'
        ]
        
        for phrase in phrases:
            if phrase in query:
                filtered_terms.extend(phrase.split())
        
        return filtered_terms
    
    def _calculate_text_similarity(self, query_terms: List[str], vehicle_text: str, preferences: Dict[str, Any]) -> float:
        """Calculate similarity between query and vehicle using multiple factors."""
        score = 0.0
        
        # Term frequency scoring
        vehicle_words = vehicle_text.split()
        vehicle_word_count = Counter(vehicle_words)
        
        # TF-IDF style scoring
        total_terms = len(query_terms)
        matched_terms = 0
        
        for term in query_terms:
            if term in vehicle_text:
                matched_terms += 1
                # Boost score based on term frequency
                tf = vehicle_word_count.get(term, 0)
                score += (1 + math.log(1 + tf)) * 0.1
        
        # Base relevance from term matching
        if total_terms > 0:
            score += (matched_terms / total_terms) * 0.4
        
        # Preference alignment boost
        if preferences:
            preference_boost = self._calculate_preference_alignment(preferences, vehicle_text)
            score += preference_boost * 0.3
        
        # Keyword importance weighting
        important_keywords = {
            'reliable': 0.15, 'dependable': 0.15, 'toyota': 0.1, 'honda': 0.1,
            'efficient': 0.12, 'hybrid': 0.12, 'electric': 0.12,
            'safe': 0.1, 'safety': 0.1, 'family': 0.08,
            'luxury': 0.1, 'premium': 0.1, 'bmw': 0.08, 'mercedes': 0.08,
            'affordable': 0.08, 'budget': 0.08, 'economical': 0.08,
            'spacious': 0.06, 'suv': 0.06, 'truck': 0.06
        }
        
        for term in query_terms:
            if term in important_keywords and term in vehicle_text:
                score += important_keywords[term]
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_preference_alignment(self, preferences: Dict[str, Any], vehicle_text: str) -> float:
        """Calculate how well vehicle aligns with extracted preferences."""
        alignment_score = 0.0
        
        # Check priority alignments
        priorities = preferences.get('priorities', [])
        
        if 'reliability' in priorities:
            if any(term in vehicle_text for term in ['reliable', 'dependable', 'toyota', 'honda']):
                alignment_score += 0.3
        
        if 'fuel_economy' in priorities:
            if any(term in vehicle_text for term in ['hybrid', 'electric', 'efficient', 'eco']):
                alignment_score += 0.3
        
        if 'safety' in priorities:
            if any(term in vehicle_text for term in ['safe', 'safety', 'family']):
                alignment_score += 0.2
        
        if 'luxury' in priorities:
            if any(term in vehicle_text for term in ['luxury', 'premium', 'bmw', 'mercedes', 'audi']):
                alignment_score += 0.3
        
        # Check vehicle type alignment
        if preferences.get('vehicle_type'):
            vehicle_type = preferences['vehicle_type']
            if vehicle_type in vehicle_text:
                alignment_score += 0.2
        
        # Check make alignment
        if preferences.get('make'):
            make = preferences['make'].lower()
            if make in vehicle_text:
                alignment_score += 0.4
        
        return alignment_score
    
    def _explain_relevance(self, query_terms: List[str], vehicle_text: str, vehicle) -> str:
        """Explain why this vehicle is relevant to the query."""
        matches = []
        
        # Find direct term matches
        for term in query_terms:
            if term in vehicle_text:
                matches.append(term)
        
        # Build explanation
        if not matches:
            return "General compatibility with your requirements"
        
        explanation_parts = []
        
        if any(term in matches for term in ['reliable', 'dependable']):
            explanation_parts.append("Known for reliability")
        
        if any(term in matches for term in ['efficient', 'hybrid', 'electric', 'eco']):
            explanation_parts.append("Excellent fuel economy")
        
        if any(term in matches for term in ['safe', 'safety', 'family']):
            explanation_parts.append("Strong safety ratings")
        
        if any(term in matches for term in ['luxury', 'premium']):
            explanation_parts.append("Premium features and comfort")
        
        if any(term in matches for term in ['budget', 'affordable', 'economical']):
            explanation_parts.append("Great value for money")
        
        # Vehicle-specific matches
        if vehicle.make.lower() in [m.lower() for m in matches]:
            explanation_parts.append(f"Matches your {vehicle.make} preference")
        
        return " • ".join(explanation_parts) if explanation_parts else f"Matches {len(matches)} of your search criteria"