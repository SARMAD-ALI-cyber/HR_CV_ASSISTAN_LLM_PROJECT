from typing import Dict, Any, Tuple, List
from cv_assistant.scoring.base_scorer import BaseScorer
from collections import Counter

class CoherenceScorer(BaseScorer):
    """Score career coherence and progression"""
    
    def calculate_score(self, cv_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate coherence score based on domain consistency and career progression
        
        Returns:
            Tuple of (score, details)
        """
        experience_items = cv_data.get("experience", [])
        education_items = cv_data.get("education", [])
        publication_items = cv_data.get("publications", [])
        
        # Need at least experience data for coherence
        if not experience_items:
            return 0.5, {  # Neutral score if no experience
                "sub_scores": {"domain_consistency": 0.5, "progression": 0.5},
                "final_score": 0.5,
                "has_data": False,
                "missing_penalty_applied": False,
                "evidence": [],
                "dominant_domain": None
            }
        
        # Get subweights
        subweights = self.config.get_subweights("coherence")
        
        # Calculate sub-scores
        domain_score = self._calculate_domain_consistency(
            experience_items, education_items, publication_items
        )
        progression_score = self._calculate_progression_score(experience_items)
        
        # Weighted combination
        final_score = (
            domain_score * subweights.get("domain_consistency", 0.6) +
            progression_score * subweights.get("progression", 0.4)
        )
        
        # Ensure score is in [0, 1]
        final_score = max(0.0, min(1.0, final_score))
        
        dominant_domain = self._get_dominant_domain(
            experience_items, education_items, publication_items
        )
        
        details = {
            "sub_scores": {
                "domain_consistency": round(domain_score, 3),
                "progression": round(progression_score, 3)
            },
            "final_score": round(final_score, 3),
            "has_data": True,
            "missing_penalty_applied": False,
            "evidence": self._get_coherence_evidence(experience_items),
            "dominant_domain": dominant_domain,
            "breakdown": self._get_breakdown(experience_items)
        }
        
        return final_score, details
    
    def _calculate_domain_consistency(
        self, 
        experience_items: List[Dict], 
        education_items: List[Dict],
        publication_items: List[Dict]
    ) -> float:
        """
        Calculate domain consistency across experience, education, and publications
        """
        domains = []
        
        # Collect domains from experience
        for exp in experience_items:
            domain = exp.get("domain", "").strip().lower()
            if domain:
                domains.append(domain)
        
        # Collect domains from education
        for edu in education_items:
            field = edu.get("field", "").strip().lower()
            if field:
                domains.append(field)
        
        # Collect domains from publications
        for pub in publication_items:
            domain = pub.get("domain", "").strip().lower()
            if domain:
                domains.append(domain)
        
        if not domains:
            return 0.5  # Neutral score if no domain info
        
        # Calculate consistency using domain frequency
        domain_counter = Counter(domains)
        most_common_domain, most_common_count = domain_counter.most_common(1)[0]
        
        # Consistency ratio
        consistency = most_common_count / len(domains)
        
        # Apply bonus if consistency meets threshold
        min_consistency = self.config.get_policy("min_domain_consistency")
        if consistency >= min_consistency:
            return min(1.0, consistency + 0.1)  # Small bonus
        
        return consistency
    
    def _calculate_progression_score(self, experience_items: List[Dict]) -> float:
        """
        Calculate career progression score
        Looks for upward trajectory in seniority and duration
        """
        if len(experience_items) < 2:
            return 0.5  # Neutral score for single job
        
        # Sort by start date (most recent first) - assuming chronological order
        # In production, you'd parse dates properly
        experiences_sorted = experience_items.copy()
        
        progression_indicators = 0
        total_comparisons = len(experiences_sorted) - 1
        
        for i in range(len(experiences_sorted) - 1):
            current_exp = experiences_sorted[i]
            previous_exp = experiences_sorted[i + 1]
            
            current_seniority = self._get_seniority_level_numeric(
                current_exp.get("title", "")
            )
            previous_seniority = self._get_seniority_level_numeric(
                previous_exp.get("title", "")
            )
            
            # Check if there's upward progression
            if current_seniority >= previous_seniority:
                progression_indicators += 1
        
        progression_ratio = progression_indicators / total_comparisons if total_comparisons > 0 else 0.5
        
        return progression_ratio
    
    def _get_seniority_level_numeric(self, title: str) -> int:
        """Convert title to numeric seniority level"""
        title_lower = title.lower()
        
        senior_keywords = ["senior", "lead", "principal", "director", "manager", "head", "chief", "vp"]
        mid_keywords = ["associate", "specialist", "analyst", "engineer", "developer", "consultant"]
        
        if any(keyword in title_lower for keyword in senior_keywords):
            return 3
        elif any(keyword in title_lower for keyword in mid_keywords):
            return 2
        else:
            return 1
    
    def _get_dominant_domain(
        self,
        experience_items: List[Dict],
        education_items: List[Dict],
        publication_items: List[Dict]
    ) -> str:
        """Identify the dominant domain across all CV sections"""
        domains = []
        
        for exp in experience_items:
            domain = exp.get("domain", "").strip()
            if domain:
                domains.append(domain)
        
        for edu in education_items:
            field = edu.get("field", "").strip()
            if field:
                domains.append(field)
        
        for pub in publication_items:
            domain = pub.get("domain", "").strip()
            if domain:
                domains.append(domain)
        
        if not domains:
            return "Unknown"
        
        domain_counter = Counter(domains)
        most_common_domain, _ = domain_counter.most_common(1)[0]
        
        return most_common_domain
    
    def _get_coherence_evidence(self, experience_items: List[Dict]) -> List[str]:
        """Get evidence of career coherence"""
        evidence = []
        
        for exp in experience_items[:3]:  # Top 3 experiences
            title = exp.get("title", "")
            org = exp.get("org", "")
            domain = exp.get("domain", "")
            evidence.append(f"{title} at {org} ({domain})")
        
        return evidence
    
    def _get_breakdown(self, experience_items: List[Dict]) -> Dict[str, Any]:
        """Get detailed breakdown of coherence factors"""
        domains = [exp.get("domain", "") for exp in experience_items if exp.get("domain")]
        domain_distribution = Counter(domains)
        
        return {
            "total_experiences": len(experience_items),
            "domain_distribution": dict(domain_distribution),
            "career_path": [
                {
                    "title": exp.get("title", ""),
                    "domain": exp.get("domain", ""),
                    "seniority": self._get_seniority_level_text(exp.get("title", ""))
                }
                for exp in experience_items
            ]
        }
    
    def _get_seniority_level_text(self, title: str) -> str:
        """Get text representation of seniority level"""
        level = self._get_seniority_level_numeric(title)
        if level == 3:
            return "Senior"
        elif level == 2:
            return "Mid"
        else:
            return "Junior"