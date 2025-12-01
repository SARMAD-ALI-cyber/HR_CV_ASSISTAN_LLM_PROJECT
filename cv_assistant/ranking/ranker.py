import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from cv_assistant import ENV

class CVRanker:
    """Rank CVs based on scores"""
    
    def __init__(self):
        self.ranked_cvs = []
    
    def rank_from_summary(self, summary_path: Path) -> List[Dict[str, Any]]:
        """
        Rank CVs from scoring summary file
        
        Args:
            summary_path: Path to scoring_summary.json
            
        Returns:
            List of CVs sorted by final_score (descending)
        """
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        scores = summary.get("scores", [])
        
        # Sort by final_score descending
        ranked = sorted(
            scores,
            key=lambda x: x.get("final_score", 0),
            reverse=True
        )
        
        # Add rank position
        for idx, cv in enumerate(ranked, start=1):
            cv["rank"] = idx
        
        self.ranked_cvs = ranked
        return ranked
    
    def rank_from_scored_cvs(self, scored_cv_dir: Path) -> List[Dict[str, Any]]:
        """
        Rank CVs from individual scored CV files
        
        Args:
            scored_cv_dir: Directory containing *_scored.json files
            
        Returns:
            List of CVs sorted by final_score (descending)
        """
        scored_files = list(scored_cv_dir.glob("*_scored.json"))
        
        all_scores = []
        for file_path in scored_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                scored_cv = json.load(f)
                all_scores.append(scored_cv.get("scoring_results", {}))
        
        # Sort by final_score descending
        ranked = sorted(
            all_scores,
            key=lambda x: x.get("final_score", 0),
            reverse=True
        )
        
        # Add rank position
        for idx, cv in enumerate(ranked, start=1):
            cv["rank"] = idx
        
        self.ranked_cvs = ranked
        return ranked
    
    def get_top_n(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get top N ranked CVs"""
        return self.ranked_cvs[:n]
    
    def get_bottom_n(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get bottom N ranked CVs"""
        return self.ranked_cvs[-n:]
    
    def get_cv_by_rank(self, rank: int) -> Dict[str, Any]:
        """Get CV at specific rank position"""
        if 1 <= rank <= len(self.ranked_cvs):
            return self.ranked_cvs[rank - 1]
        return None
    
    def get_cv_by_filename(self, filename: str) -> Tuple[int, Dict[str, Any]]:
        """
        Get CV and its rank by filename
        
        Returns:
            Tuple of (rank, cv_data)
        """
        for cv in self.ranked_cvs:
            if cv.get("cv_filename") == filename:
                return cv.get("rank"), cv
        return None, None
    
    def save_ranked_list(self, output_path: Path):
        """
        Save ranked list to JSON file
        
        Args:
            output_path: Path to save ranked_candidates.json
        """
        ranked_output = {
            "total_candidates": len(self.ranked_cvs),
            "ranking_date": self._get_timestamp(),
            "ranked_candidates": self.ranked_cvs
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ranked_output, f, indent=2, ensure_ascii=False)
    
    def generate_ranking_report(self,number_of_candidates_to_Rank) -> Dict[str, Any]:
        """Generate statistical report on rankings"""
        if not self.ranked_cvs:
            return {}
        
        scores = [cv.get("final_score", 0) for cv in self.ranked_cvs]
        
        # Calculate statistics
        mean_score = sum(scores) / len(scores)
        sorted_scores = sorted(scores)
        median_score = sorted_scores[len(sorted_scores) // 2]
        
        # Standard deviation
        variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
        std_dev = variance ** 0.5

        distribution = {
            "0.0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0
        }
        
        for score in scores:
            if score < 0.2:
                distribution["0.0-0.2"] += 1
            elif score < 0.4:
                distribution["0.2-0.4"] += 1
            elif score < 0.6:
                distribution["0.4-0.6"] += 1
            elif score < 0.8:
                distribution["0.6-0.8"] += 1
            else:
                distribution["0.8-1.0"] += 1
        
        return {
            "total_candidates": len(self.ranked_cvs),
            "statistics": {
                "mean_score": round(mean_score, 4),
                "median_score": round(median_score, 4),
                "std_deviation": round(std_dev, 4),
                "min_score": round(min(scores), 4),
                "max_score": round(max(scores), 4)
            },
            "score_distribution": distribution,
            f"top_{number_of_candidates_to_Rank}": [
                {
                    "rank": cv.get("rank"),
                    "filename": cv.get("cv_filename"),
                    "score": cv.get("final_score_percentage")
                }
                for cv in self.ranked_cvs[:number_of_candidates_to_Rank]
            ]
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


_ranker_instance = None

def get_ranker() -> CVRanker:
    """Get global ranker instance (singleton)"""
    global _ranker_instance
    if _ranker_instance is None:
        _ranker_instance = CVRanker()
    return _ranker_instance