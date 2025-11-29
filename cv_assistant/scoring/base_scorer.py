from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

class BaseScorer(ABC):
    """Base class for all scorers"""
    
    def __init__(self, config, mapping_utils):
        """
        Initialize scorer
        
        Args:
            config: ConfigLoader instance
            mapping_utils: MappingUtils instance
        """
        self.config = config
        self.mapping_utils = mapping_utils
    
    @abstractmethod
    def calculate_score(self, cv_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate score for this criterion
        
        Args:
            cv_data: Parsed CV data (education, experience, publications, awards)
            
        Returns:
            Tuple of (score, details_dict) where:
                - score: float between 0 and 1
                - details_dict: breakdown of how score was calculated
        """
        pass
    
    def normalize_score(self, value: float, max_value: float) -> float:
        """
        Normalize a value to 0-1 range
        
        Args:
            value: Raw value to normalize
            max_value: Maximum expected value
            
        Returns:
            float: Normalized score between 0 and 1
        """
        if max_value == 0:
            return 0.0
        return min(1.0, value / max_value)
    
    def apply_missing_penalty(self, score: float, has_data: bool) -> float:
        """
        Apply penalty for missing data
        
        Args:
            score: Current score
            has_data: Whether data exists for this criterion
            
        Returns:
            float: Score after penalty
        """
        if not has_data:
            penalty = self.config.get_policy("missing_values_penalty")
            return max(0.0, score - penalty)
        return score
    
    def get_evidence_spans(self, items: List[Dict[str, Any]], limit: int = 3) -> List[str]:
        """
        Extract evidence spans from items
        
        Args:
            items: List of items (education, experience, etc.)
            limit: Maximum number of evidence spans to return
            
        Returns:
            List of evidence span strings
        """
        evidence = []
        for item in items[:limit]:
            if "evidence_span" in item and item["evidence_span"]:
                evidence.append(item["evidence_span"][:200])  # Truncate long spans
        return evidence