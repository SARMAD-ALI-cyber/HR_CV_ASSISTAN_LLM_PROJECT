from typing import Dict, Any, Tuple, List
from cv_assistant.scoring.base_scorer import BaseScorer

class PublicationScorer(BaseScorer):
    """Score research publications"""
    
    def calculate_score(self, cv_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate publication score based on IF, author position, and venue quality
        
        Returns:
            Tuple of (score, details)
        """
        publication_items = cv_data.get("publications", [])
        
        if not publication_items:
            return 0.0, {
                "sub_scores": {"if": 0.0, "author_position": 0.0, "venue_quality": 0.0},
                "final_score": 0.0,
                "has_data": False,
                "missing_penalty_applied": True,
                "evidence": [],
                "total_publications": 0
            }
        
        # Get subweights
        subweights = self.config.get_subweights("publications")
        
        # Calculate sub-scores
        if_score = self._calculate_if_score(publication_items)
        author_score = self._calculate_author_position_score(publication_items)
        venue_score = self._calculate_venue_score(publication_items)
        
        # Weighted combination
        final_score = (
            if_score * subweights.get("if", 0.5) +
            author_score * subweights.get("author_position", 0.3) +
            venue_score * subweights.get("venue_quality", 0.2)
        )
        
        # Ensure score is in [0, 1]
        final_score = max(0.0, min(1.0, final_score))
        
        details = {
            "sub_scores": {
                "if": round(if_score, 3),
                "author_position": round(author_score, 3),
                "venue_quality": round(venue_score, 3)
            },
            "final_score": round(final_score, 3),
            "has_data": True,
            "missing_penalty_applied": False,
            "evidence": self.get_evidence_spans(publication_items),
            "total_publications": len(publication_items),
            "breakdown": self._get_breakdown(publication_items)
        }
        
        return final_score, details
    
    def _calculate_if_score(self, publication_items: List[Dict]) -> float:
        """Calculate average normalized Impact Factor score"""
        if not publication_items:
            return 0.0
        
        total_if = 0.0
        count = 0
        max_if = self.config.get_normalization("max_journal_if")
        
        for pub in publication_items:
            # Try to get IF from the publication data
            if_value = pub.get("journal_if")
            
            # If not in CV, look it up from mapping
            if not if_value:
                venue = pub.get("venue", "")
                pub_type = pub.get("type", "").lower()
                
                if "journal" in pub_type:
                    if_value = self.mapping_utils.get_journal_if(venue)
                else:
                    # For conferences, use venue quality as proxy
                    venue_quality = self.mapping_utils.get_venue_quality_score(venue)
                    # Convert venue quality (0-1) to IF-like scale
                    if_value = venue_quality * 10  # Scale to 0-10 range
            
            if if_value:
                normalized_if = self.normalize_score(if_value, max_if)
                total_if += normalized_if
                count += 1
        
        return total_if / count if count > 0 else 0.0
    
    def _calculate_author_position_score(self, publication_items: List[Dict]) -> float:
        """Calculate author position score with bonuses for first/second author"""
        if not publication_items:
            return 0.0
        
        position_scores = []
        
        for pub in publication_items:
            position = pub.get("author_position", 999)
            
            if position == 1:
                # First author - highest score + bonus
                bonus = self.config.get_policy("first_author_bonus")
                position_scores.append(min(1.0, 1.0 + bonus))
            elif position == 2:
                # Second author - high score + smaller bonus
                bonus = self.config.get_policy("second_author_bonus")
                position_scores.append(min(1.0, 0.8 + bonus))
            elif position <= 5:
                # Top 5 authors - decreasing score
                position_scores.append(0.6 - (position - 3) * 0.1)
            else:
                # Beyond 5th position - minimal score
                position_scores.append(0.2)
        
        return sum(position_scores) / len(position_scores) if position_scores else 0.0
    
    def _calculate_venue_score(self, publication_items: List[Dict]) -> float:
        """Calculate average venue quality score"""
        if not publication_items:
            return 0.0
        
        venue_scores = []
        
        for pub in publication_items:
            venue = pub.get("venue", "")
            pub_type = pub.get("type", "").lower()
            
            if "journal" in pub_type:
                # For journals, use IF as proxy for quality
                if_value = self.mapping_utils.get_journal_if(venue)
                # Normalize IF to 0-1 scale (assuming max IF of 50)
                venue_score = min(1.0, if_value / 50.0)
            else:
                # For conferences, use venue quality mapping
                venue_score = self.mapping_utils.get_venue_quality_score(venue)
            
            venue_scores.append(venue_score)
        
        return sum(venue_scores) / len(venue_scores) if venue_scores else 0.0
    
    def _get_breakdown(self, publication_items: List[Dict]) -> List[Dict]:
        """Get detailed breakdown for each publication"""
        breakdown = []
        
        for pub in publication_items:
            venue = pub.get("venue", "")
            pub_type = pub.get("type", "").lower()
            
            # Get IF or venue quality
            if "journal" in pub_type:
                quality_metric = self.mapping_utils.get_journal_if(venue)
                quality_type = "IF"
            else:
                quality_metric = self.mapping_utils.get_venue_quality_score(venue)
                quality_type = "Venue Score"
            
            breakdown.append({
                "title": pub.get("title", ""),
                "venue": venue,
                "year": pub.get("year", ""),
                "type": pub.get("type", ""),
                "author_position": pub.get("author_position", "Unknown"),
                "quality_metric": round(quality_metric, 2),
                "quality_type": quality_type,
                "domain": pub.get("domain", "")
            })
        
        return breakdown