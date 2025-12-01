from typing import Dict, Any, List
from cv_assistant.ranking import get_comparator

class ExplanationGenerator:
    """Generate human-readable explanations for CV rankings"""
    
    def __init__(self):
        self.comparator = get_comparator()
    
    def explain_why_a_better_than_b(
        self, 
        cv_a: Dict[str, Any], 
        cv_b: Dict[str, Any],
        include_evidence: bool = True
    ) -> Dict[str, Any]:
        """
        Generate explanation for why CV A ranks higher than CV B
        
        Args:
            cv_a: Higher ranked CV scoring results
            cv_b: Lower ranked CV scoring results
            include_evidence: Whether to include evidence spans
            
        Returns:
            Explanation dictionary with reasons and evidence
        """
        
        comparison = self.comparator.compare(cv_a, cv_b)
        
      
        key_differences = comparison.get("key_differences", [])
        
        # Generate top 3 reasons
        reasons = self._generate_reasons(key_differences, cv_a, cv_b)
        

        if include_evidence:
            reasons = self._add_evidence_to_reasons(reasons, cv_a, cv_b)
        
        explanation = {
            "summary": self._generate_summary(cv_a, cv_b, comparison),
            "top_reasons": reasons,
            "delta_table": comparison.get("delta_table", []),
            "overall_delta": comparison.get("overall_delta", {}),
            "cv_a_filename": cv_a.get("cv_filename", "Unknown"),
            "cv_b_filename": cv_b.get("cv_filename", "Unknown")
        }
        
        return explanation
    
    def _generate_summary(
        self, 
        cv_a: Dict[str, Any], 
        cv_b: Dict[str, Any],
        comparison: Dict[str, Any]
    ) -> str:
        """Generate a summary statement"""
        filename_a = cv_a.get("cv_filename", "Candidate A")
        filename_b = cv_b.get("cv_filename", "Candidate B")
        score_a = cv_a.get("final_score_percentage", 0)
        score_b = cv_b.get("final_score_percentage", 0)
        delta = comparison.get("overall_delta", {}).get("percentage", 0)
        
        summary = (
            f"{filename_a} (Score: {score_a:.2f}%) ranks higher than "
            f"{filename_b} (Score: {score_b:.2f}%) by {abs(delta):.2f} percentage points. "
        )
        
   
        key_diff = comparison.get("key_differences", [{}])[0]
        if key_diff:
            criterion = key_diff.get("criterion", "").replace("_", " ").title()
            summary += f"The primary advantage is in {criterion}."
        
        return summary
    
    def _generate_reasons(
        self, 
        key_differences: List[Dict[str, Any]],
        cv_a: Dict[str, Any],
        cv_b: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate top 3 reasons with human-readable text"""
        reasons = []
        
        for idx, diff in enumerate(key_differences[:3], start=1):
            criterion = diff.get("criterion", "")
            contribution_delta = diff.get("contribution_delta", 0)
            score_delta = diff.get("score_delta", 0)
            
            # Get details from CV A and B
            criteria_a = cv_a.get("criterion_scores", {}).get(criterion, {})
            criteria_b = cv_b.get("criterion_scores", {}).get(criterion, {})
            
            reason_text = self._generate_reason_text(
                criterion, 
                score_delta, 
                contribution_delta,
                criteria_a,
                criteria_b
            )
            
            reasons.append({
                "rank": idx,
                "criterion": criterion.replace("_", " ").title(),
                "reason": reason_text,
                "score_delta": round(score_delta, 4),
                "contribution_delta": round(contribution_delta, 4),
                "impact": "High" if abs(contribution_delta) > 0.1 else "Medium" if abs(contribution_delta) > 0.05 else "Low"
            })
        
        return reasons
    
    def _generate_reason_text(
        self,
        criterion: str,
        score_delta: float,
        contribution_delta: float,
        details_a: Dict[str, Any],
        details_b: Dict[str, Any]
    ) -> str:
        """Generate human-readable reason text for a criterion"""
        
        criterion_name = criterion.replace("_", " ").title()
        
        if criterion == "education":
            return self._explain_education(details_a, details_b, score_delta)
        elif criterion == "experience":
            return self._explain_experience(details_a, details_b, score_delta)
        elif criterion == "publications":
            return self._explain_publications(details_a, details_b, score_delta)
        elif criterion == "coherence":
            return self._explain_coherence(details_a, details_b, score_delta)
        elif criterion == "awards_other":
            return self._explain_awards(details_a, details_b, score_delta)
        else:
            return f"{criterion_name} is stronger by {abs(score_delta):.2%}"
    
    def _explain_education(self, details_a: Dict, details_b: Dict, delta: float) -> str:
        """Explain education difference"""
        sub_a = details_a.get("details", {}).get("sub_scores", {})
        sub_b = details_b.get("details", {}).get("sub_scores", {})
        
        gpa_delta = sub_a.get("gpa", 0) - sub_b.get("gpa", 0)
        tier_delta = sub_a.get("university_tier", 0) - sub_b.get("university_tier", 0)
        degree_delta = sub_a.get("degree_level", 0) - sub_b.get("degree_level", 0)
        
        reasons = []
        if tier_delta > 0.1:
            reasons.append("higher-tier university")
        if gpa_delta > 0.1:
            reasons.append("better GPA")
        if degree_delta > 0.1:
            reasons.append("higher degree level")
        
        if reasons:
            return f"Stronger education due to {', '.join(reasons)}."
        return f"Better overall education profile (score advantage: {delta:.2%})."
    
    def _explain_experience(self, details_a: Dict, details_b: Dict, delta: float) -> str:
        """Explain experience difference"""
        months_a = details_a.get("details", {}).get("total_months", 0)
        months_b = details_b.get("details", {}).get("total_months", 0)
        
        sub_a = details_a.get("details", {}).get("sub_scores", {})
        sub_b = details_b.get("details", {}).get("sub_scores", {})
        
        duration_delta = sub_a.get("duration", 0) - sub_b.get("duration", 0)
        domain_delta = sub_a.get("domain_match", 0) - sub_b.get("domain_match", 0)
        seniority_delta = sub_a.get("seniority", 0) - sub_b.get("seniority", 0)
        
        reasons = []
        if duration_delta > 0.1:
            years_diff = (months_a - months_b) / 12
            reasons.append(f"{years_diff:.1f} more years of experience")
        if domain_delta > 0.1:
            reasons.append("better domain alignment")
        if seniority_delta > 0.1:
            reasons.append("higher seniority level")
        
        if reasons:
            return f"Stronger experience: {', '.join(reasons)}."
        return f"Better overall experience profile (score advantage: {delta:.2%})."
    
    def _explain_publications(self, details_a: Dict, details_b: Dict, delta: float) -> str:
        """Explain publications difference"""
        count_a = details_a.get("details", {}).get("total_publications", 0)
        count_b = details_b.get("details", {}).get("total_publications", 0)
        
        sub_a = details_a.get("details", {}).get("sub_scores", {})
        sub_b = details_b.get("details", {}).get("sub_scores", {})
        
        if_delta = sub_a.get("if", 0) - sub_b.get("if", 0)
        author_delta = sub_a.get("author_position", 0) - sub_b.get("author_position", 0)
        venue_delta = sub_a.get("venue_quality", 0) - sub_b.get("venue_quality", 0)
        
        reasons = []
        if count_a > count_b:
            reasons.append(f"{count_a - count_b} more publications")
        if if_delta > 0.1:
            reasons.append("higher impact factor journals")
        if author_delta > 0.1:
            reasons.append("better author positions")
        if venue_delta > 0.1:
            reasons.append("higher-quality venues")
        
        if reasons:
            return f"Stronger research profile: {', '.join(reasons)}."
        return f"Better publication record (score advantage: {delta:.2%})."
    
    def _explain_coherence(self, details_a: Dict, details_b: Dict, delta: float) -> str:
        """Explain coherence difference"""
        domain_a = details_a.get("details", {}).get("dominant_domain", "")
        domain_b = details_b.get("details", {}).get("dominant_domain", "")
        
        sub_a = details_a.get("details", {}).get("sub_scores", {})
        sub_b = details_b.get("details", {}).get("sub_scores", {})
        
        consistency_delta = sub_a.get("domain_consistency", 0) - sub_b.get("domain_consistency", 0)
        progression_delta = sub_a.get("progression", 0) - sub_b.get("progression", 0)
        
        reasons = []
        if consistency_delta > 0.1:
            reasons.append("more consistent domain focus")
        if progression_delta > 0.1:
            reasons.append("better career progression")
        
        if reasons:
            return f"Better career coherence: {', '.join(reasons)}."
        return f"More coherent career trajectory (score advantage: {delta:.2%})."
    
    def _explain_awards(self, details_a: Dict, details_b: Dict, delta: float) -> str:
        """Explain awards difference"""
        count_a = details_a.get("details", {}).get("total_awards", 0)
        count_b = details_b.get("details", {}).get("total_awards", 0)
        
        if count_a > count_b:
            return f"{count_a - count_b} more awards and achievements."
        elif count_a == count_b and count_a > 0:
            return "Higher quality awards."
        return f"Better awards profile (score advantage: {delta:.2%})."
    
    def _add_evidence_to_reasons(
        self,
        reasons: List[Dict[str, Any]],
        cv_a: Dict[str, Any],
        cv_b: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Add evidence spans to reasons"""
        for reason in reasons:
            criterion = reason.get("criterion", "").lower().replace(" ", "_")
            
            # Get evidence from CV A
            criteria_a = cv_a.get("criterion_scores", {}).get(criterion, {})
            evidence_a = criteria_a.get("details", {}).get("evidence", [])
            
            # Get evidence from CV B
            criteria_b = cv_b.get("criterion_scores", {}).get(criterion, {})
            evidence_b = criteria_b.get("details", {}).get("evidence", [])
            
            reason["evidence"] = {
                "cv_a": evidence_a[:2],  # Top 2 evidence spans
                "cv_b": evidence_b[:2]
            }
        
        return reasons



_explanation_generator_instance = None

def get_explanation_generator() -> ExplanationGenerator:
    """Get global explanation generator instance (singleton)"""
    global _explanation_generator_instance
    if _explanation_generator_instance is None:
        _explanation_generator_instance = ExplanationGenerator()
    return _explanation_generator_instance