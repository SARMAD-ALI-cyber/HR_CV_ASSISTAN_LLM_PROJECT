from typing import Dict, Any,List
from cv_assistant.config import get_config
from cv_assistant.mappings import get_mapping_utils
from cv_assistant.scoring.education_scorer import EducationScorer
from cv_assistant.scoring.experience_scorer import ExperienceScorer
from cv_assistant.scoring.publication_scorer import PublicationScorer
from cv_assistant.scoring.coherence_scorer import CoherenceScorer
from cv_assistant.scoring.awards_scorer import AwardsScorer

class ScoreAggregator:
    """Aggregate all scores into final CV score"""
    
    def __init__(self, config=None, mapping_utils=None):
        """
        Initialize aggregator with all scorers
        
        Args:
            config: ConfigLoader instance (uses global if None)
            mapping_utils: MappingUtils instance (uses global if None)
        """
        self.config = config or get_config()
        self.mapping_utils = mapping_utils or get_mapping_utils()
        
        # Initialize all scorers
        self.education_scorer = EducationScorer(self.config, self.mapping_utils)
        self.experience_scorer = ExperienceScorer(self.config, self.mapping_utils)
        self.publication_scorer = PublicationScorer(self.config, self.mapping_utils)
        self.coherence_scorer = CoherenceScorer(self.config, self.mapping_utils)
        self.awards_scorer = AwardsScorer(self.config, self.mapping_utils)
    
    def calculate_final_score(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate final weighted score for a CV
        
        Args:
            cv_data: Parsed CV data with education, experience, publications, awards
            
        Returns:
            Dict with final score and detailed breakdown
        """
        # Get main weights
        weights = self.config.get_all_weights()
        
        # Calculate individual criterion scores
        education_score, education_details = self.education_scorer.calculate_score(cv_data)
        experience_score, experience_details = self.experience_scorer.calculate_score(cv_data)
        publication_score, publication_details = self.publication_scorer.calculate_score(cv_data)
        coherence_score, coherence_details = self.coherence_scorer.calculate_score(cv_data)
        awards_score, awards_details = self.awards_scorer.calculate_score(cv_data)
        
        # Calculate weighted final score
        final_score = (
            education_score * weights.get("education", 0.3) +
            experience_score * weights.get("experience", 0.3) +
            publication_score * weights.get("publications", 0.25) +
            coherence_score * weights.get("coherence", 0.1) +
            awards_score * weights.get("awards_other", 0.05)
        )
        
        # Ensure score is in [0, 1]
        final_score = max(0.0, min(1.0, final_score))
        
        # Compile detailed results
        results = {
            "final_score": round(final_score, 4),
            "final_score_percentage": round(final_score * 100, 2),
            "criterion_scores": {
                "education": {
                    "score": round(education_score, 4),
                    "weight": weights.get("education", 0.3),
                    "weighted_contribution": round(education_score * weights.get("education", 0.3), 4),
                    "details": education_details
                },
                "experience": {
                    "score": round(experience_score, 4),
                    "weight": weights.get("experience", 0.3),
                    "weighted_contribution": round(experience_score * weights.get("experience", 0.3), 4),
                    "details": experience_details
                },
                "publications": {
                    "score": round(publication_score, 4),
                    "weight": weights.get("publications", 0.25),
                    "weighted_contribution": round(publication_score * weights.get("publications", 0.25), 4),
                    "details": publication_details
                },
                "coherence": {
                    "score": round(coherence_score, 4),
                    "weight": weights.get("coherence", 0.1),
                    "weighted_contribution": round(coherence_score * weights.get("coherence", 0.1), 4),
                    "details": coherence_details
                },
                "awards_other": {
                    "score": round(awards_score, 4),
                    "weight": weights.get("awards_other", 0.05),
                    "weighted_contribution": round(awards_score * weights.get("awards_other", 0.05), 4),
                    "details": awards_details
                }
            },
            "config_used": {
                "weights": weights,
                "target_domain": self.config.get_policy("target_domain")
            }
        }
        
        return results
    
    def score_cv_file(self, cv_json_path: str) -> Dict[str, Any]:
        """
        Score a CV from JSON file
        
        Args:
            cv_json_path: Path to CV JSON file
            
        Returns:
            Scoring results
        """
        import json
        from pathlib import Path
        
        cv_path = Path(cv_json_path)
        
        if not cv_path.exists():
            raise FileNotFoundError(f"CV file not found: {cv_json_path}")
        
        with open(cv_path, 'r', encoding='utf-8') as f:
            cv_data = json.load(f)
        
        # Calculate scores
        results = self.calculate_final_score(cv_data)
        
        # Add metadata
        results["cv_filename"] = cv_path.stem
        results["cv_path"] = str(cv_path)
        
        return results
    
    def get_top_strengths(self, scoring_results: Dict[str, Any], top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Identify top N strengths from scoring results
        
        Args:
            scoring_results: Results from calculate_final_score
            top_n: Number of top strengths to return
            
        Returns:
            List of top strengths with scores
        """
        criterion_scores = scoring_results.get("criterion_scores", {})
        
        # Sort by weighted contribution
        sorted_criteria = sorted(
            criterion_scores.items(),
            key=lambda x: x[1].get("weighted_contribution", 0),
            reverse=True
        )
        
        top_strengths = []
        for criterion, data in sorted_criteria[:top_n]:
            top_strengths.append({
                "criterion": criterion,
                "score": data.get("score"),
                "contribution": data.get("weighted_contribution"),
                "has_data": data.get("details", {}).get("has_data", False)
            })
        
        return top_strengths
    
    def get_improvement_areas(self, scoring_results: Dict[str, Any], bottom_n: int = 2) -> List[Dict[str, Any]]:
        """
        Identify areas for improvement
        
        Args:
            scoring_results: Results from calculate_final_score
            bottom_n: Number of improvement areas to return
            
        Returns:
            List of improvement areas
        """
        criterion_scores = scoring_results.get("criterion_scores", {})
        
        # Sort by score (ascending)
        sorted_criteria = sorted(
            criterion_scores.items(),
            key=lambda x: x[1].get("score", 0)
        )
        
        improvement_areas = []
        for criterion, data in sorted_criteria[:bottom_n]:
            improvement_areas.append({
                "criterion": criterion,
                "score": data.get("score"),
                "has_data": data.get("details", {}).get("has_data", False),
                "missing": not data.get("details", {}).get("has_data", False)
            })
        
        return improvement_areas


# Global instance
_aggregator_instance = None

def get_aggregator() -> ScoreAggregator:
    """Get global aggregator instance (singleton)"""
    global _aggregator_instance
    if _aggregator_instance is None:
        _aggregator_instance = ScoreAggregator()
    return _aggregator_instance