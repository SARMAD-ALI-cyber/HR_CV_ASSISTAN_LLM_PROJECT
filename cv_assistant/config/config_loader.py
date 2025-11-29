import yaml
import json
from pathlib import Path
from typing import Dict, Any
from cv_assistant import ENV

class ConfigLoader:
    """Load and validate configuration for CV scoring"""
    
    def __init__(self, config_path: Path = None):
        """
        Initialize config loader
        
        Args:
            config_path: Path to config file. If None, uses default_config.yaml
        """
        if config_path is None:

            config_path = ENV.CONFIG_DIR / "default_config.yaml"
        
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            if self.config_path.suffix == '.yaml' or self.config_path.suffix == '.yml':
                config = yaml.safe_load(f)
            elif self.config_path.suffix == '.json':
                config = json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {self.config_path.suffix}")
        
        return config
    
    def _validate_config(self):
        """Validate configuration structure and values"""
        # Check main weights sum to 1.0
        weights = self.config.get('weights', {})
        weight_sum = sum(weights.values())
        
        if not (0.99 <= weight_sum <= 1.01):  # Allow small floating point errors
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")
        
        # Check required sections exist
        required_sections = ['weights', 'subweights', 'policies', 'normalization']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
        
        # Check subweights for each criterion
        for criterion in weights.keys():
            if criterion != 'awards_other' and criterion != 'coherence':
                if criterion not in self.config['subweights']:
                    raise ValueError(f"Missing subweights for criterion: {criterion}")
    
    def get_weight(self, criterion: str) -> float:
        """Get weight for a criterion"""
        return self.config['weights'].get(criterion, 0.0)
    
    def get_subweights(self, criterion: str) -> Dict[str, float]:
        """Get subweights for a criterion"""
        return self.config['subweights'].get(criterion, {})
    
    def get_policy(self, policy_name: str) -> Any:
        """Get a policy parameter"""
        return self.config['policies'].get(policy_name)
    
    def get_normalization(self, param_name: str) -> float:
        """Get normalization parameter"""
        return self.config['normalization'].get(param_name, 1.0)
    
    def get_all_weights(self) -> Dict[str, float]:
        """Get all main weights"""
        return self.config['weights']
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get complete configuration"""
        return self.config
    
    def save_config(self, output_path: Path):
        """Save current configuration to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False)



_config_instance = None

def get_config(config_path: Path = None) -> ConfigLoader:
    """Get global config instance (singleton pattern)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance

def reload_config(config_path: Path = None):
    """Reload configuration"""
    global _config_instance
    _config_instance = ConfigLoader(config_path)