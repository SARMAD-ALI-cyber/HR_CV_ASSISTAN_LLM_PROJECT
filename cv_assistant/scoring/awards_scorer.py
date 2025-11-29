from typing import Dict, Any, Tuple, List
from cv_assistant.scoring.base_scorer import BaseScorer

class AwardsScorer(BaseScorer):
    """Score awards and achievements"""
    
    def calculate_score(self, cv_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate awards score based on number and prestige of awards
        
        Returns:
            Tuple of (score, details)
        """
        awards_items = cv_data.get("awards", [])
        
        if not awards_items:
            return 0.0, {
                "final_score": 0.0,
                "has_data": False,
                "missing_penalty_applied": False,  # No penalty for missing awards
                "evidence": [],
                "total_awards": 0
            }
        
        # Calculate score based on number and type of awards
        score = self._calculate_awards_score(awards_items)
        
        # Ensure score is in [0, 1]
        score = max(0.0, min(1.0, score))
        
        details = {
            "final_score": round(score, 3),
            "has_data": True,
            "missing_penalty_applied": False,
            "evidence": self.get_evidence_spans(awards_items),
            "total_awards": len(awards_items),
            "breakdown": self._get_breakdown(awards_items)
        }
        
        return score, details
    
    def _calculate_awards_score(self, awards_items: List[Dict]) -> float:
        """
        Calculate awards score based on quantity and quality
        """
        if not awards_items:
            return 0.0
        
        total_score = 0.0
        
        for award in awards_items:
            award_type = award.get("type", "").lower()
            title = award.get("title", "").lower()
            issuer = award.get("issuer", "").lower()
            
            # Base score for having an award
            award_score = 0.3
            
            # Higher score for specific types
            if any(keyword in award_type for keyword in ["research", "academic", "professional"]):
                award_score = 0.6
            
            if any(keyword in award_type for keyword in ["national", "international"]):
                award_score = 0.8
            
            # Bonus for prestigious awards
            prestigious_keywords = [
                "gold", "medal", "best", "outstanding", "excellence",
                "dean's list", "honors", "scholarship", "fellowship",
                "distinguished", "achievement", "recognition"
            ]
            
            if any(keyword in title for keyword in prestigious_keywords):
                award_score += 0.2
            
            # Bonus for prestigious issuers
            prestigious_issuers = [
                "ieee", "acm", "google", "microsoft", "amazon",
                "national", "international", "government"
            ]
            
            if any(keyword in issuer for keyword in prestigious_issuers):
                award_score += 0.1
            
            # Cap individual award score at 1.0
            award_score = min(1.0, award_score)
            
            total_score += award_score
        
        # Normalize by number of awards (diminishing returns)
        # Use logarithmic scaling to prevent excessive scores
        import math
        normalized_score = math.log(1 + total_score) / math.log(1 + len(awards_items) * 1.5)
        
        return min(1.0, normalized_score)
    
    def _get_breakdown(self, awards_items: List[Dict]) -> List[Dict]:
        """Get detailed breakdown for each award"""
        breakdown = []
        
        for award in awards_items:
            breakdown.append({
                "title": award.get("title", ""),
                "issuer": award.get("issuer", ""),
                "year": award.get("year", ""),
                "type": award.get("type", ""),
                "prestige_level": self._assess_prestige(award)
            })
        
        return breakdown
    
    def _assess_prestige(self, award: Dict) -> str:
        """Assess prestige level of an award"""
        title = award.get("title", "").lower()
        award_type = award.get("type", "").lower()
        issuer = award.get("issuer", "").lower()
        
        # High prestige indicators
        high_prestige = [
            "gold", "medal", "best", "outstanding", "excellence",
            "national", "international", "distinguished"
        ]
        
        # Medium prestige indicators
        medium_prestige = [
            "dean's list", "honors", "scholarship", "fellowship",
            "achievement", "recognition", "academic", "professional"
        ]
        
        if any(keyword in title or keyword in award_type or keyword in issuer 
               for keyword in high_prestige):
            return "High"
        elif any(keyword in title or keyword in award_type or keyword in issuer 
                 for keyword in medium_prestige):
            return "Medium"
        else:
            return "Standard"