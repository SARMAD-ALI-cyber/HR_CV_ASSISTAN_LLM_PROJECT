from typing import Dict, Any, Tuple, List
from cv_assistant.scoring.base_scorer import BaseScorer

class EducationScorer(BaseScorer):
    """Score education background"""
    
    def calculate_score(self, cv_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate education score based on GPA, degree level, and university tier
        
        Returns:
            Tuple of (score, details)
        """
        education_items = cv_data.get("education", [])
        
        if not education_items:
            return 0.0, {
                "sub_scores": {"gpa": 0.0, "degree_level": 0.0, "university_tier": 0.0},
                "final_score": 0.0,
                "has_data": False,
                "missing_penalty_applied": True,
                "evidence": []
            }
        
        # Get subweights
        subweights = self.config.get_subweights("education")
        
        # Calculate sub-scores
        gpa_score = self._calculate_gpa_score(education_items)
        degree_score = self._calculate_degree_score(education_items)
        university_score = self._calculate_university_score(education_items)
        
        # Weighted combination
        final_score = (
            gpa_score * subweights.get("gpa", 0.5) +
            degree_score * subweights.get("degree_level", 0.2) +
            university_score * subweights.get("university_tier", 0.3)
        )
        
        # Apply bonuses
        final_score = self._apply_bonuses(final_score, education_items)
        
        # Ensure score is in [0, 1]
        final_score = max(0.0, min(1.0, final_score))
        
        details = {
            "sub_scores": {
                "gpa": round(gpa_score, 3),
                "degree_level": round(degree_score, 3),
                "university_tier": round(university_score, 3)
            },
            "final_score": round(final_score, 3),
            "has_data": True,
            "missing_penalty_applied": False,
            "evidence": self.get_evidence_spans(education_items),
            "breakdown": self._get_breakdown(education_items)
        }
        
        return final_score, details
    
    def _calculate_gpa_score(self, education_items: List[Dict]) -> float:
        """Calculate normalized GPA score (highest GPA taken)"""
        if not education_items:
            return 0.0
        
        max_normalized_gpa = 0.0
        
        for edu in education_items:
            gpa = edu.get("gpa", 0.0)
            scale = edu.get("scale", 4.0)
            
            if gpa and scale and scale > 0:
                # Normalize to 0-1 scale
                normalized = gpa / scale
                max_normalized_gpa = max(max_normalized_gpa, normalized)
        
        return max_normalized_gpa
    
    def _calculate_degree_score(self, education_items: List[Dict]) -> float:
        """Calculate degree level score (highest degree taken)"""
        if not education_items:
            return 0.0
        
        max_level = 0
        
        for edu in education_items:
            degree = edu.get("degree", "")
            level = self.mapping_utils.get_degree_level_score(degree)
            max_level = max(max_level, level)
        
        # Normalize: BSc=1 -> 0.33, MSc=2 -> 0.67, PhD=3 -> 1.0
        return (max_level - 1) / 2.0 if max_level > 0 else 0.0
    
    def _calculate_university_score(self, education_items: List[Dict]) -> float:
        """Calculate university tier score (highest tier taken)"""
        if not education_items:
            return 0.0
        
        max_tier_score = 0.0
        
        for edu in education_items:
            university = edu.get("university", "")
            tier_score = self.mapping_utils.get_university_tier_score(university)
            max_tier_score = max(max_tier_score, tier_score)
        
        return max_tier_score
    
    def _apply_bonuses(self, base_score: float, education_items: List[Dict]) -> float:
        """Apply bonuses for PhD and Master's degrees"""
        has_phd = False
        has_masters = False
        
        for edu in education_items:
            degree = edu.get("degree", "").lower()
            if "phd" in degree or "doctorate" in degree:
                has_phd = True
            elif "msc" in degree or "master" in degree or "ms" in degree:
                has_masters = True
        
        score = base_score
        
        if has_phd:
            phd_bonus = self.config.get_policy("phd_bonus")
            score += phd_bonus
        elif has_masters:
            masters_bonus = self.config.get_policy("masters_bonus")
            score += masters_bonus
        
        return score
    
    def _get_breakdown(self, education_items: List[Dict]) -> List[Dict]:
        """Get detailed breakdown for each education entry"""
        breakdown = []
        
        for edu in education_items:
            breakdown.append({
                "degree": edu.get("degree", ""),
                "university": edu.get("university", ""),
                "gpa": f"{edu.get('gpa', 0)}/{edu.get('scale', 4)}",
                "tier_score": self.mapping_utils.get_university_tier_score(edu.get("university", "")),
                "degree_level": self.mapping_utils.get_degree_level_score(edu.get("degree", ""))
            })
        
        return breakdown