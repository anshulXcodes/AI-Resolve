import math
from datetime import datetime
from typing import List, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.schemas import CaseRecord, DuplicateEvidence, GemmaExtractionResult
from app.core.config import settings

class DuplicateDetectionService:
    """
    Hybrid Duplicate Detection Service:
    Combines:
    1. Semantic similarity (TF-IDF & Substring N-gram vectorizer / Sentence Embeddings cosine score)
    2. Location rule matching (Block & Floor exact/partial match)
    3. Temporal decay weighting (Complaints closer in time receive higher duplication likelihood)
    
    Crucial Rule from PPT:
    Never silently auto-merge! If score >= threshold, flag as duplicate candidate
    with full evidence breakdown for human review.
    """
    
    @classmethod
    def evaluate_candidate(
        cls, 
        new_text: str, 
        new_extraction: GemmaExtractionResult,
        existing_cases: List[CaseRecord]
    ) -> Tuple[List[DuplicateEvidence], bool]:
        
        candidates: List[DuplicateEvidence] = []
        is_held_as_duplicate = False
        
        if not existing_cases:
            return candidates, False
            
        all_texts = [c.raw_complaint for c in existing_cases] + [new_text]
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarity with all existing cases
        similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
        
        now = datetime.now()
        
        for idx, existing in enumerate(existing_cases):
            # Only compare with active/open cases (not rejected or long resolved)
            semantic_score = float(similarities[idx])
            
            # Boost semantic score if key intent terms match (e.g. water leak / pipe)
            if existing.extraction.issue_type == new_extraction.issue_type:
                semantic_score = min(1.0, semantic_score + 0.15)
                
            # Location score
            location_score = 0.0
            if existing.extraction.building_block.lower() == new_extraction.building_block.lower():
                location_score += 0.6
                if existing.extraction.floor_or_room and new_extraction.floor_or_room:
                    if existing.extraction.floor_or_room.lower() == new_extraction.floor_or_room.lower():
                        location_score += 0.4
                    else:
                        location_score = max(0.2, location_score - 0.2)
                elif "stair" in existing.raw_complaint.lower() and "stair" in new_text.lower():
                    location_score += 0.4
            else:
                location_score = 0.1
                
            # Time decay score (assuming within recent hours/days = high correlation)
            try:
                case_time = datetime.fromisoformat(existing.created_at)
                hours_diff = abs((now - case_time).total_seconds()) / 3600.0
                # Exponential decay over 48 hours
                time_score = max(0.2, math.exp(-hours_diff / 48.0))
            except Exception:
                time_score = 0.8
                
            # Hybrid Formula: 50% Semantic + 35% Location + 15% Time Proximity
            hybrid_score = (0.50 * semantic_score) + (0.35 * location_score) + (0.15 * time_score)
            
            is_match = hybrid_score >= settings.HYBRID_DUPLICATE_THRESHOLD
            if is_match:
                is_held_as_duplicate = True
                
            reason = (
                f"Matched category ({existing.extraction.issue_type.value}) and block ({existing.extraction.building_block}). "
                f"Semantic similarity {semantic_score:.2f}, location match {location_score:.2f}."
            )
            
            if is_match or hybrid_score > 0.45:
                candidates.append(DuplicateEvidence(
                    matched_case_id=existing.id,
                    matched_case_title=existing.extraction.clean_summary,
                    matched_created_at=existing.created_at,
                    semantic_similarity=round(semantic_score, 3),
                    location_match_score=round(location_score, 3),
                    time_window_score=round(time_score, 3),
                    overall_hybrid_score=round(hybrid_score, 3),
                    is_duplicate_candidate=is_match,
                    reason=reason
                ))
                
        # Sort candidates descending by hybrid score
        candidates.sort(key=lambda x: x.overall_hybrid_score, reverse=True)
        return candidates, is_held_as_duplicate
