import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from cv_assistant import ENV

class GroundTruthManager:
    """Manage ground truth rankings and pairwise preferences"""
    
    def __init__(self, annotations_dir: Path = None):
        """
        Initialize ground truth manager
        
        Args:
            annotations_dir: Directory for annotation files
        """
        if annotations_dir is None:
            annotations_dir = ENV.ANNOTATIONS_DIR
            
        
        self.annotations_dir = annotations_dir
        self.ground_truth_file = annotations_dir / "ground_truth.json"
        self.pairwise_file = annotations_dir / "pairwise_preferences.json"
    
    def create_sample_ground_truth(self, ranked_cvs: List[Dict[str, Any]], sample_size: int = 20):
        """
        Create a sample ground truth file from top-ranked CVs
        (In production, this would be manually annotated by HR)
        
        Args:
            ranked_cvs: List of ranked CV scoring results
            sample_size: Number of CVs to include in ground truth
        """
        # Take top N CVs as pseudo ground truth
        sample_cvs = ranked_cvs[:sample_size]
        
        ground_truth = {
            "description": "Ground truth ranking (sample-for demonstration purposes)",
            "sample_size": len(sample_cvs),
            "ranking": [cv.get("cv_filename") for cv in sample_cvs],
            "relevance_scores": {
                cv.get("cv_filename"): cv.get("final_score", 0)
                for cv in sample_cvs
            }
        }
        
        with open(self.ground_truth_file, 'w', encoding='utf-8') as f:
            json.dump(ground_truth, f, indent=2, ensure_ascii=False)
        
        return ground_truth
    
    def create_sample_pairwise_preferences(self, ranked_cvs: List[Dict[str, Any]], num_pairs: int = 50):
        """
        Create sample pairwise preferences
        (In production, these would be HR's actual pairwise judgments)
        
        Args:
            ranked_cvs: List of ranked CV scoring results
            num_pairs: Number of pairs to generate
        """
        import random
        
        pairwise_preferences = []
        
        # Generate pairs with significant rank differences
        for i in range(min(num_pairs, len(ranked_cvs) - 1)):
            # Pick pairs that are at least 2-3 ranks apart
            idx_a = i
            idx_b = min(i + random.randint(2, 5), len(ranked_cvs) - 1)
            
            if idx_b < len(ranked_cvs):
                cv_a = ranked_cvs[idx_a]
                cv_b = ranked_cvs[idx_b]
                
                pairwise_preferences.append({
                    "better": cv_a.get("cv_filename"),
                    "worse": cv_b.get("cv_filename"),
                    "reason": f"Higher overall score ({cv_a.get('final_score_percentage', 0):.2f}% vs {cv_b.get('final_score_percentage', 0):.2f}%)"
                })
        
        pairwise_data = {
            "description": "Pairwise preferences (sample-for demonstration purposes)",
            "total_pairs": len(pairwise_preferences),
            "pairs": pairwise_preferences
        }
        
        with open(self.pairwise_file, 'w', encoding='utf-8') as f:
            json.dump(pairwise_data, f, indent=2, ensure_ascii=False)
        
        return pairwise_data
    
    def load_ground_truth(self) -> Dict[str, Any]:
        """Load ground truth ranking"""
        if not self.ground_truth_file.exists():
            return None
        
        with open(self.ground_truth_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_pairwise_preferences(self) -> List[Tuple[str, str]]:
        """
        Load pairwise preferences
        
        Returns:
            List of (better_cv, worse_cv) tuples
        """
        if not self.pairwise_file.exists():
            return []
        
        with open(self.pairwise_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pairs = []
        for pair in data.get("pairs", []):
            pairs.append((pair.get("better"), pair.get("worse")))
        
        return pairs
    
    def get_relevance_scores(self) -> Dict[str, float]:
        """Get relevance scores from ground truth"""
        ground_truth = self.load_ground_truth()
        if ground_truth:
            return ground_truth.get("relevance_scores", {})
        return {}
    
    def get_ground_truth_ranking(self) -> List[str]:
        """Get ground truth ranking as ordered list"""
        ground_truth = self.load_ground_truth()
        if ground_truth:
            return ground_truth.get("ranking", [])
        return []



_ground_truth_manager = None

def get_ground_truth_manager() -> GroundTruthManager:
    global _ground_truth_manager
    if _ground_truth_manager is None:
        _ground_truth_manager = GroundTruthManager()
    return _ground_truth_manager