from typing import Dict, Any, List, Tuple

class CVComparator:
    """Compare two CVs and generate delta analysis"""
    
    def compare(self, cv_a: Dict[str, Any], cv_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two CVs and generate detailed comparison
        
        Args:
            cv_a: First CV's scoring results
            cv_b: Second CV's scoring results
            
        Returns:
            Comparison dictionary with deltas and analysis
        """

        score_a = cv_a.get("final_score", 0)
        score_b = cv_b.get("final_score", 0)
        overall_delta = score_a - score_b
        

        criteria_a = cv_a.get("criterion_scores", {})
        criteria_b = cv_b.get("criterion_scores", {})
        
 
        criterion_deltas = self._calculate_criterion_deltas(criteria_a, criteria_b)

        key_differences = self._identify_key_differences(criterion_deltas)
        

        winner = "A" if overall_delta > 0 else "B" if overall_delta < 0 else "Tie"
        
        comparison = {
            "cv_a": {
                "filename": cv_a.get("cv_filename", "Unknown"),
                "final_score": score_a,
                "final_score_percentage": cv_a.get("final_score_percentage", score_a * 100)
            },
            "cv_b": {
                "filename": cv_b.get("cv_filename", "Unknown"),
                "final_score": score_b,
                "final_score_percentage": cv_b.get("final_score_percentage", score_b * 100)
            },
            "overall_delta": {
                "absolute": round(overall_delta, 4),
                "percentage": round(overall_delta * 100, 2),
                "winner": winner
            },
            "criterion_deltas": criterion_deltas,
            "key_differences": key_differences,
            "delta_table": self._create_delta_table(criteria_a, criteria_b)
        }
        
        return comparison
    
    def _calculate_criterion_deltas(
        self, 
        criteria_a: Dict[str, Any], 
        criteria_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate deltas for each criterion"""
        deltas = {}
        
        for criterion in ["education", "experience", "publications", "coherence", "awards_other"]:
            score_a = criteria_a.get(criterion, {}).get("score", 0)
            score_b = criteria_b.get(criterion, {}).get("score", 0)
            contribution_a = criteria_a.get(criterion, {}).get("weighted_contribution", 0)
            contribution_b = criteria_b.get(criterion, {}).get("weighted_contribution", 0)
            
            deltas[criterion] = {
                "score_delta": round(score_a - score_b, 4),
                "contribution_delta": round(contribution_a - contribution_b, 4),
                "a_score": round(score_a, 4),
                "b_score": round(score_b, 4),
                "a_contribution": round(contribution_a, 4),
                "b_contribution": round(contribution_b, 4)
            }
        
        return deltas
    
    def _identify_key_differences(self, criterion_deltas: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify top 3 key differences by contribution delta
        
        Returns:
            List of top 3 differences sorted by absolute contribution delta
        """
        differences = []
        
        for criterion, delta_data in criterion_deltas.items():
            differences.append({
                "criterion": criterion,
                "contribution_delta": delta_data["contribution_delta"],
                "score_delta": delta_data["score_delta"],
                "abs_contribution_delta": abs(delta_data["contribution_delta"])
            })
        
        # Sort by absolute contribution delta (descending)
        differences.sort(key=lambda x: x["abs_contribution_delta"], reverse=True)
        
        # Return top 3
        return differences[:3]
    
    def _create_delta_table(
        self, 
        criteria_a: Dict[str, Any], 
        criteria_b: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create a formatted delta table for display
        
        Returns:
            List of rows for delta table
        """
        table_rows = []
        
        for criterion in ["education", "experience", "publications", "coherence", "awards_other"]:
            score_a = criteria_a.get(criterion, {}).get("score", 0)
            score_b = criteria_b.get(criterion, {}).get("score", 0)
            weight = criteria_a.get(criterion, {}).get("weight", 0)
            contribution_a = criteria_a.get(criterion, {}).get("weighted_contribution", 0)
            contribution_b = criteria_b.get(criterion, {}).get("weighted_contribution", 0)
            
            delta_score = score_a - score_b
            delta_contribution = contribution_a - contribution_b
            
            table_rows.append({
                "criterion": criterion.replace("_", " ").title(),
                "weight": round(weight, 2),
                "cv_a_score": round(score_a, 4),
                "cv_b_score": round(score_b, 4),
                "score_delta": round(delta_score, 4),
                "cv_a_contribution": round(contribution_a, 4),
                "cv_b_contribution": round(contribution_b, 4),
                "contribution_delta": round(delta_contribution, 4),
                "winner": "A" if delta_contribution > 0 else "B" if delta_contribution < 0 else "Tie"
            })
        
        return table_rows
    
    def compare_pairwise(self, cv_a: Dict[str, Any], cv_b: Dict[str, Any]) -> int:
        """
        Simple pairwise comparison
        
        Args:
            cv_a: First CV
            cv_b: Second CV
            
        Returns:
            1 if A > B, -1 if B > A, 0 if tie
        """
        score_a = cv_a.get("final_score", 0)
        score_b = cv_b.get("final_score", 0)
        
        if score_a > score_b:
            return 1
        elif score_b > score_a:
            return -1
        else:
            return 0


_comparator_instance = None

def get_comparator() -> CVComparator:
    """Get global comparator instance (singleton)"""
    global _comparator_instance
    if _comparator_instance is None:
        _comparator_instance = CVComparator()
    return _comparator_instance