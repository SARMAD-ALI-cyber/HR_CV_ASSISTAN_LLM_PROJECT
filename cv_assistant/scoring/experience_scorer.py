from typing import Dict, Any, Tuple, List
from cv_assistant.scoring.base_scorer import BaseScorer
import re

class ExperienceScorer(BaseScorer):
    """Score work experience"""
    
    def calculate_score(self, cv_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate experience score based on duration, domain match, and seniority
        
        Returns:
            Tuple of (score, details)
        """
        experience_items = cv_data.get("experience", [])
        
        if not experience_items:
            return 0.0, {
                "sub_scores": {"duration": 0.0, "domain_match": 0.0, "seniority": 0.0},
                "final_score": 0.0,
                "has_data": False,
                "missing_penalty_applied": True,
                "evidence": [],
                "total_months": 0
            }
        
        # Get subweights
        subweights = self.config.get_subweights("experience")
        
        # Calculate sub-scores
        duration_score = self._calculate_duration_score(experience_items)
        domain_score = self._calculate_domain_score(experience_items)
        seniority_score = self._calculate_seniority_score(experience_items)
        
        # Weighted combination
        final_score = (
            duration_score * subweights.get("duration", 0.5) +
            domain_score * subweights.get("domain_match", 0.3) +
            seniority_score * subweights.get("seniority", 0.2)
        )
        
        # Apply experience bonus
        total_months = self._calculate_total_months(experience_items)
        final_score = self._apply_experience_bonus(final_score, total_months)
        
        # Ensure score is in [0, 1]
        final_score = max(0.0, min(1.0, final_score))
        
        details = {
            "sub_scores": {
                "duration": round(duration_score, 3),
                "domain_match": round(domain_score, 3),
                "seniority": round(seniority_score, 3)
            },
            "final_score": round(final_score, 3),
            "has_data": True,
            "missing_penalty_applied": False,
            "evidence": self.get_evidence_spans(experience_items),
            "total_months": total_months,
            "total_years": round(total_months / 12, 1),
            "breakdown": self._get_breakdown(experience_items)
        }
        
        return final_score, details
    
    def _calculate_total_months(self, experience_items: List[Dict]) -> int:
        """Calculate total months of experience"""
        total_months = 0
        
        for exp in experience_items:
            duration = exp.get("duration_months")
            if duration and isinstance(duration, (int, float)):
                total_months += int(duration)
            else:
                # Try to estimate from dates if duration is missing
                total_months += self._estimate_duration(exp)
        
        return total_months
    
    def _estimate_duration(self, exp: Dict) -> int:
        """Estimate duration from start/end dates if duration_months is missing"""
        # This is a simplified estimation
        # In production, you'd want more robust date parsing
        start = exp.get("start", "")
        end = exp.get("end", "")
        
        # If end is "Current" or "Present", assume it's ongoing (12 months as estimate)
        if end and any(keyword in end.lower() for keyword in ["current", "present", "now"]):
            return 12
        
        # Otherwise, return 0 (will be handled as missing)
        return 0
    
    def _calculate_duration_score(self, experience_items: List[Dict]) -> float:
        """Calculate normalized duration score"""
        total_months = self._calculate_total_months(experience_items)
        max_months = self.config.get_normalization("max_experience_months")
        
        return self.normalize_score(total_months, max_months)
    
    def _calculate_domain_score(self, experience_items: List[Dict]) -> float:
        """Calculate domain match score"""
        target_domain = self.config.get_policy("target_domain")
        
        if not target_domain:
            return 0.5  # Neutral score if no target domain specified
        
        domain_matches = 0
        total_experiences = len(experience_items)
        
        for exp in experience_items:
            exp_domain = exp.get("domain", "").lower()
            if target_domain.lower() in exp_domain:
                domain_matches += 1
        
        if total_experiences == 0:
            return 0.0
        
        match_ratio = domain_matches / total_experiences
        
        # Apply domain match bonus if high match
        if match_ratio >= 0.5:
            bonus = self.config.get_policy("domain_match_bonus")
            return min(1.0, match_ratio + bonus)
        
        return match_ratio
    
    def _calculate_seniority_score(self, experience_items: List[Dict]) -> float:
        """Calculate seniority score based on job titles"""
        max_seniority = 0
        
        senior_keywords = ["senior", "lead", "principal", "director", "manager", "head", "chief", "vp"]
        mid_keywords = ["associate", "specialist", "analyst", "engineer", "developer"]
        
        for exp in experience_items:
            title = exp.get("title", "").lower()
            
            if any(keyword in title for keyword in senior_keywords):
                max_seniority = max(max_seniority, 3)
            elif any(keyword in title for keyword in mid_keywords):
                max_seniority = max(max_seniority, 2)
            else:
                max_seniority = max(max_seniority, 1)
        
        # Normalize: Junior=1 -> 0.33, Mid=2 -> 0.67, Senior=3 -> 1.0
        return (max_seniority - 1) / 2.0 if max_seniority > 0 else 0.0
    
    def _apply_experience_bonus(self, base_score: float, total_months: int) -> float:
        """Apply bonus for meeting experience threshold"""
        min_months = self.config.get_policy("min_months_experience_for_bonus")
        
        if total_months >= min_months:
            bonus = self.config.get_policy("experience_bonus")
            return base_score + bonus
        
        return base_score
    
    def _get_breakdown(self, experience_items: List[Dict]) -> List[Dict]:
        """Get detailed breakdown for each experience entry"""
        breakdown = []
        
        for exp in experience_items:
            duration = exp.get("duration_months", 0)
            if not duration:
                duration = self._estimate_duration(exp)
            
            breakdown.append({
                "title": exp.get("title", ""),
                "org": exp.get("org", ""),
                "duration_months": duration,
                "domain": exp.get("domain", ""),
                "seniority_level": self._get_seniority_level(exp.get("title", ""))
            })
        
        return breakdown
    
    def _get_seniority_level(self, title: str) -> str:
        """Determine seniority level from title"""
        title_lower = title.lower()
        
        senior_keywords = ["senior", "lead", "principal", "director", "manager", "head", "chief", "vp"]
        mid_keywords = ["associate", "specialist", "analyst", "engineer", "developer"]
        
        if any(keyword in title_lower for keyword in senior_keywords):
            return "Senior"
        elif any(keyword in title_lower for keyword in mid_keywords):
            return "Mid"
        else:
            return "Junior"