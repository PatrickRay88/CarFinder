"""Recommendation engine for vehicle suggestions."""
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class ScoringWeights:
    """Weights for different scoring factors."""
    price: float = 0.3
    reliability: float = 0.25
    fuel_efficiency: float = 0.2
    safety: float = 0.15
    features: float = 0.1

class RecommendationEngine:
    """Multi-objective vehicle recommendation engine."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Reliability scores by make (simplified)
        self.reliability_scores = {
            'toyota': 0.95, 'honda': 0.92, 'mazda': 0.88, 'subaru': 0.85,
            'hyundai': 0.82, 'kia': 0.80, 'ford': 0.75, 'chevrolet': 0.72,
            'bmw': 0.70, 'mercedes-benz': 0.68, 'audi': 0.66, 'volkswagen': 0.64
        }
    
    def recommend(self, search_results: List[Dict[str, Any]], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations from search results."""
        
        if not search_results:
            return []
        
        # Extract weights from preferences
        weights = self._get_scoring_weights(preferences)
        
        # Score each vehicle
        scored_vehicles = []
        for result in search_results:
            vehicle = result['vehicle']
            base_score = result.get('score', 1.0)  # RAG similarity score
            
            # Calculate multi-objective score
            objective_score = self._calculate_objective_score(vehicle, preferences, weights)
            
            # Combine RAG and objective scores
            final_score = 0.4 * base_score + 0.6 * objective_score
            
            # Generate explanation
            explanation = self._generate_explanation(vehicle, preferences, weights)
            
            scored_vehicles.append({
                'vehicle': vehicle,
                'score': final_score,
                'base_score': base_score,
                'objective_score': objective_score,
                'explanation': explanation,
                'scores_breakdown': self._get_scores_breakdown(vehicle, preferences, weights)
            })
        
        # Sort by final score
        scored_vehicles.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_vehicles
    
    def _get_scoring_weights(self, preferences: Dict[str, Any]) -> ScoringWeights:
        """Extract and normalize scoring weights from preferences."""
        user_weights = preferences.get('weights', {})
        
        weights = ScoringWeights(
            price=user_weights.get('price', 0.3),
            reliability=user_weights.get('reliability', 0.25),
            fuel_efficiency=user_weights.get('fuel_efficiency', 0.2),
            safety=user_weights.get('safety', 0.15),
            features=user_weights.get('features', 0.1)
        )
        
        # Normalize weights to sum to 1
        total = weights.price + weights.reliability + weights.fuel_efficiency + weights.safety + weights.features
        if total > 0:
            weights.price /= total
            weights.reliability /= total
            weights.fuel_efficiency /= total
            weights.safety /= total
            weights.features /= total
        
        return weights
    
    def _calculate_objective_score(self, vehicle: Dict[str, Any], preferences: Dict[str, Any], weights: ScoringWeights) -> float:
        """Calculate multi-objective score for a vehicle."""
        
        scores = {
            'price': self._score_price(vehicle, preferences),
            'reliability': self._score_reliability(vehicle),
            'fuel_efficiency': self._score_fuel_efficiency(vehicle),
            'safety': self._score_safety(vehicle),
            'features': self._score_features(vehicle, preferences)
        }
        
        # Calculate weighted score
        total_score = (
            weights.price * scores['price'] +
            weights.reliability * scores['reliability'] +
            weights.fuel_efficiency * scores['fuel_efficiency'] +
            weights.safety * scores['safety'] +
            weights.features * scores['features']
        )
        
        return max(0, min(1, total_score))
    
    def _score_price(self, vehicle: Dict[str, Any], preferences: Dict[str, Any]) -> float:
        """Score vehicle based on price preference."""
        price = vehicle.get('price')
        if not price:
            return 0.5  # Neutral score for unknown price
        
        budget_max = preferences.get('budget_max')
        if not budget_max:
            return 0.8  # Good score if no budget constraint
        
        # Score based on how well it fits budget
        if price <= budget_max * 0.7:  # Well under budget
            return 1.0
        elif price <= budget_max * 0.9:  # Comfortably within budget
            return 0.9
        elif price <= budget_max:  # Just within budget
            return 0.7
        elif price <= budget_max * 1.1:  # Slightly over budget
            return 0.4
        else:  # Significantly over budget
            return 0.1
    
    def _score_reliability(self, vehicle: Dict[str, Any]) -> float:
        """Score vehicle based on reliability."""
        make = vehicle.get('make', '').lower()
        base_score = self.reliability_scores.get(make, 0.6)  # Default average
        
        # Adjust for age
        year = vehicle.get('year', 2020)
        current_year = 2024
        age = current_year - year
        
        if age <= 2:
            age_multiplier = 1.0
        elif age <= 5:
            age_multiplier = 0.95
        elif age <= 8:
            age_multiplier = 0.85
        else:
            age_multiplier = 0.7
        
        # Adjust for mileage
        mileage = vehicle.get('mileage', 50000)
        if mileage <= 30000:
            mileage_multiplier = 1.0
        elif mileage <= 60000:
            mileage_multiplier = 0.95
        elif mileage <= 100000:
            mileage_multiplier = 0.85
        else:
            mileage_multiplier = 0.7
        
        return base_score * age_multiplier * mileage_multiplier
    
    def _score_fuel_efficiency(self, vehicle: Dict[str, Any]) -> float:
        """Score vehicle based on fuel efficiency."""
        mpg_city = vehicle.get('mpg_city', 0)
        mpg_highway = vehicle.get('mpg_highway', 0)
        
        if not mpg_city or not mpg_highway:
            return 0.5  # Neutral for unknown
        
        avg_mpg = (mpg_city + mpg_highway) / 2
        
        # Score based on MPG ranges
        if avg_mpg >= 40:  # Excellent
            return 1.0
        elif avg_mpg >= 30:  # Good
            return 0.8
        elif avg_mpg >= 25:  # Average
            return 0.6
        elif avg_mpg >= 20:  # Below average
            return 0.4
        else:  # Poor
            return 0.2
    
    def _score_safety(self, vehicle: Dict[str, Any]) -> float:
        """Score vehicle based on safety rating."""
        safety_rating = vehicle.get('safety_rating')
        if not safety_rating:
            return 0.6  # Neutral for unknown
        
        return safety_rating / 5.0  # Normalize to 0-1 scale
    
    def _score_features(self, vehicle: Dict[str, Any], preferences: Dict[str, Any]) -> float:
        """Score vehicle based on desired features match."""
        vehicle_features = set(vehicle.get('features', []))
        desired_features = set(preferences.get('desired_features', []))
        
        if not desired_features:
            return 0.8  # Good score if no specific requirements
        
        if not vehicle_features:
            return 0.3  # Low score for no features listed
        
        # Calculate feature match ratio
        matched_features = vehicle_features.intersection(desired_features)
        match_ratio = len(matched_features) / len(desired_features)
        
        # Bonus for having extra desirable features
        common_desirable = {'backup camera', 'bluetooth', 'navigation', 'heated seats'}
        bonus_features = vehicle_features.intersection(common_desirable)
        bonus_score = len(bonus_features) * 0.05  # 5% bonus per feature
        
        return min(1.0, match_ratio + bonus_score)
    
    def _generate_explanation(self, vehicle: Dict[str, Any], preferences: Dict[str, Any], weights: ScoringWeights) -> str:
        """Generate human-readable explanation for recommendation."""
        explanations = []
        
        # Price explanation
        if weights.price > 0.2:
            price = vehicle.get('price')
            budget_max = preferences.get('budget_max')
            if price and budget_max:
                if price <= budget_max * 0.8:
                    explanations.append("excellent value within your budget")
                elif price <= budget_max:
                    explanations.append("fits comfortably in your budget")
        
        # Reliability explanation
        if weights.reliability > 0.2:
            make = vehicle.get('make', '').lower()
            if make in ['toyota', 'honda', 'mazda']:
                explanations.append(f"{make.title()} has excellent reliability ratings")
        
        # Fuel efficiency explanation
        if weights.fuel_efficiency > 0.2:
            mpg_city = vehicle.get('mpg_city', 0)
            mpg_highway = vehicle.get('mpg_highway', 0)
            if mpg_city and mpg_highway:
                avg_mpg = (mpg_city + mpg_highway) / 2
                if avg_mpg >= 30:
                    explanations.append(f"excellent fuel economy ({avg_mpg:.1f} MPG average)")
        
        # Safety explanation
        if weights.safety > 0.15:
            safety_rating = vehicle.get('safety_rating')
            if safety_rating and safety_rating >= 4:
                explanations.append(f"high safety rating ({safety_rating}/5 stars)")
        
        # Features explanation
        desired_features = preferences.get('desired_features', [])
        vehicle_features = vehicle.get('features', [])
        if desired_features and vehicle_features:
            matched = set(vehicle_features).intersection(set(desired_features))
            if matched:
                explanations.append(f"includes {len(matched)} of your desired features")
        
        if not explanations:
            return "Good overall match for your preferences"
        
        return "Great choice because it offers " + ", ".join(explanations) + "."
    
    def _get_scores_breakdown(self, vehicle: Dict[str, Any], preferences: Dict[str, Any], weights: ScoringWeights) -> Dict[str, float]:
        """Get detailed score breakdown for transparency."""
        return {
            'price_score': self._score_price(vehicle, preferences),
            'reliability_score': self._score_reliability(vehicle),
            'fuel_efficiency_score': self._score_fuel_efficiency(vehicle),
            'safety_score': self._score_safety(vehicle),
            'features_score': self._score_features(vehicle, preferences),
            'price_weight': weights.price,
            'reliability_weight': weights.reliability,
            'fuel_efficiency_weight': weights.fuel_efficiency,
            'safety_weight': weights.safety,
            'features_weight': weights.features
        }