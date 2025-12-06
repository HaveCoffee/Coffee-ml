import numpy as np
from sentence_transformers import SentenceTransformer,util


def calculate_interest_score(user_a_intersts: list[int], user_b_intersts: list[int]) -> float:
    """
    Calculates the interest similarity score between two users based on their interest IDs.
    Uses Jaccard similarity as the metric.
    """
    set_a = set(user_a_intersts)
    set_b = set(user_b_intersts)
    
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    
    if union == 0:
        return 0.0
    
    score = intersection / union
    return score

def calculate_availability_score(user_a_availability: dict, user_b_availability: dict ) -> float:
    if not user_a_availability or not user_b_availability:
        return 0.0
    score = 0.0
    days_a=set(user_a_availability.get('days',[]))
    days_b=set(user_b_availability.get('days',[]))
    if days_a.intersection(days_b):
        score += 0.5
    time_a=set(user_a_availability.get('time_slots',[]))
    time_b=set(user_b_availability.get('time_slots',[]))
    if time_a.intersection(time_b):
        score += 0.5
    
    return score

def calculate_location_score(user_a_coords, user_b_coords) -> float:
    """Calculates a location score. Placeholder for now."""
    # For now, we will return a default score until geocoding is implemented.
    # In the future, this would calculate Haversine distance.
    return 0.5

def calculate_personality_score(user_a_embedding: np.ndarray, user_b_embedding: np.ndarray) -> float:
    """Calculates the Cosine Similarity between two profile embeddings."""
    if user_a_embedding is None or user_b_embedding is None:
        return 0.0
        
    cosine_score = util.cos_sim(user_a_embedding, user_b_embedding).item()
    return max(0, cosine_score)

def calculate_final_match_score(profile_a, profile_b) -> float:
    """
    Calculates the final weighted match score based on the four pillars.
    """
    interests_a = profile_a.profile_data.get('interest_ids', [])
    interests_b = profile_b.profile_data.get('interest_ids', [])
    interest_score = calculate_interest_score(interests_a, interests_b)

    availability_a = profile_a.profile_data.get('availability', {})
    availability_b = profile_b.profile_data.get('availability', {})
    availability_score = calculate_availability_score(availability_a, availability_b)

    location_score = calculate_location_score(None, None)
    personality_score = calculate_personality_score(profile_a.embedding, profile_b.embedding)

    final_score = (
        0.40 * interest_score +
        0.30 * availability_score +
        0.20 * location_score +
        0.10 * personality_score
    )
    
    return final_score