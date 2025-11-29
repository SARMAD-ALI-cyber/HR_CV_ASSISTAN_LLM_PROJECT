import json
from pathlib import Path
from typing import Optional, Dict, Any
from cv_assistant import ENV
from fuzzywuzzy import fuzz

class MappingUtils:
    """Utilities for looking up university tiers, journal IFs, and venue quality"""
    
    def __init__(self):
        self.mappings_dir = ENV.MAPPINGS_DIR
        
        
        self.university_tiers = self._load_json("university_tiers.json")
        self.journal_if = self._load_json("journal_if.json")
        self.venue_quality = self._load_json("venue_quality.json")
        
        # Build reverse lookup for faster searching
        self._build_university_lookup()
        self._build_venue_lookup()
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load a JSON mapping file"""
        file_path = self.mappings_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Mapping file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_university_lookup(self):
        """Build reverse lookup for universities"""
        self.university_lookup = {}
        for tier_name, tier_data in self.university_tiers.items():
            if tier_name == "default_tier":
                continue
            score = tier_data["score"]
            for uni in tier_data["universities"]:
                self.university_lookup[uni.lower()] = score
    
    def _build_venue_lookup(self):
        """Build reverse lookup for venues"""
        self.venue_lookup = {}
        for tier_name, tier_data in self.venue_quality.items():
            if tier_name in ["default_venue", "preprints"]:
                if tier_name == "preprints":
                    for venue in tier_data["venues"]:
                        self.venue_lookup[venue.lower()] = tier_data["score"]
                continue
            score = tier_data["score"]
            for venue in tier_data["venues"]:
                self.venue_lookup[venue.lower()] = score
    
    def get_university_tier_score(self, university_name: str) -> float:
        """
        Get tier score for a university
        
        Args:
            university_name: Name of the university
            
        Returns:
            float: Score between 0 and 1
        """
        if not university_name:
            return self.university_tiers["default_tier"]["score"]
        
        # Exact match (case-insensitive)
        uni_lower = university_name.lower()
        if uni_lower in self.university_lookup:
            return self.university_lookup[uni_lower]
        
        # Fuzzy matching for partial matches
        best_score = self.university_tiers["default_tier"]["score"]
        best_ratio = 0
        
        for uni_key, score in self.university_lookup.items():
            ratio = fuzz.token_set_ratio(uni_lower, uni_key)
            if ratio > 85 and ratio > best_ratio:  # 85% similarity threshold
                best_ratio = ratio
                best_score = score
        
        return best_score
    
    def get_journal_if(self, journal_name: str) -> float:
        """
        Get Impact Factor for a journal
        
        Args:
            journal_name: Name of the journal
            
        Returns:
            float: Impact Factor
        """
        if not journal_name:
            return self.journal_if["default_if"]
        
        # Exact match (case-insensitive)
        journals = self.journal_if.get("journals", {})
        
        # Try exact match first
        for journal_key, if_value in journals.items():
            if journal_name.lower() == journal_key.lower():
                return if_value
        
        # Fuzzy matching
        best_if = self.journal_if["default_if"]
        best_ratio = 0
        
        for journal_key, if_value in journals.items():
            ratio = fuzz.token_set_ratio(journal_name.lower(), journal_key.lower())
            if ratio > 85 and ratio > best_ratio:
                best_ratio = ratio
                best_if = if_value
        
        return best_if
    
    def get_venue_quality_score(self, venue_name: str) -> float:
        """
        Get quality score for a conference/venue
        
        Args:
            venue_name: Name of the venue/conference
            
        Returns:
            float: Score between 0 and 1
        """
        if not venue_name:
            return self.venue_quality["default_venue"]["score"]
        
        venue_lower = venue_name.lower()
        
        # Exact match
        if venue_lower in self.venue_lookup:
            return self.venue_lookup[venue_lower]
        
        # Check for preprints
        for preprint_keyword in ["arxiv", "biorxiv", "medrxiv", "preprint", "ssrn"]:
            if preprint_keyword in venue_lower:
                return self.venue_quality["preprints"]["score"]
        
        # Fuzzy matching
        best_score = self.venue_quality["default_venue"]["score"]
        best_ratio = 0
        
        for venue_key, score in self.venue_lookup.items():
            ratio = fuzz.token_set_ratio(venue_lower, venue_key)
            if ratio > 85 and ratio > best_ratio:
                best_ratio = ratio
                best_score = score
        
        return best_score
    
    def get_degree_level_score(self, degree: str) -> int:
        """
        Get numeric score for degree level
        
        Args:
            degree: Degree name (e.g., "BSc", "MSc", "PhD")
            
        Returns:
            int: 1 for Bachelor's, 2 for Master's, 3 for PhD
        """
        if not degree:
            return 1
        
        degree_lower = degree.lower()
        

        if any(keyword in degree_lower for keyword in ["phd", "ph.d", "doctorate", "doctoral"]):
            return 3

        if any(keyword in degree_lower for keyword in ["msc", "ms", "ma", "master", "mphil"]):
            return 2
        
        # Bachelor's level (default)
        return 1



_mapping_utils_instance = None

def get_mapping_utils() -> MappingUtils:
    """Get global mapping utils instance (singleton)"""
    global _mapping_utils_instance
    if _mapping_utils_instance is None:
        _mapping_utils_instance = MappingUtils()
    return _mapping_utils_instance