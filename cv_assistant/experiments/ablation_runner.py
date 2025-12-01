import json
from pathlib import Path
from typing import List, Dict, Any
from cv_assistant import ENV
from cv_assistant.config import ConfigLoader
from cv_assistant.scoring import ScoreAggregator
from cv_assistant.ranking import CVRanker
from cv_assistant.evaluation import get_ranking_metrics, get_ground_truth_manager
from cv_assistant.utils.logger import info, success, warn
from cv_assistant.utils.status import get_progress_bar

class AblationRunner:
    """Run ablation studies with different configurations"""
    
    def __init__(self, json_dir: Path = None, output_dir: Path = None):
        """
        Initialize ablation runner
        
        Args:
            json_dir: Directory with extracted CV JSONs
            output_dir: Output directory for ablation results
        """
        self.json_dir = json_dir or ENV.JSON_DIR
        self.output_dir = output_dir or (ENV.ABLATIONS_DIR)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Load CV data once
        self.cv_data = self._load_all_cvs()
    
    def _load_all_cvs(self) -> List[Dict[str, Any]]:
        """Load all CV JSONs"""
        cv_files = list(self.json_dir.glob("*.json"))
        cvs = []
        
        for cv_file in cv_files:
            with open(cv_file, 'r', encoding='utf-8') as f:
                cv_data = json.load(f)
                cvs.append({
                    "filename": cv_file.stem,
                    "data": cv_data
                })
        
        return cvs
    
    def run_ablation(
        self,
        ablation_name: str,
        config_path: Path,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Run a single ablation study
        
        Args:
            ablation_name: Name of ablation
            config_path: Path to configuration file for this ablation
            description: Description of what's being tested
            
        Returns:
            Ablation results
        """
        info(f"Running ablation: {ablation_name}")
        info(f"Description: {description}")
        
        # Load config for this ablation
        config = ConfigLoader(config_path)
        
        # Score all CVs with this config
        aggregator = ScoreAggregator(config=config, mapping_utils=None)
        
        scored_results = []
        
        with get_progress_bar() as progress:
            scoring_task = progress.add_task(
                description=f"[yellow]Scoring with {ablation_name}...",
                total=len(self.cv_data)
            )
            
            for cv in self.cv_data:
                scoring_result = aggregator.calculate_final_score(cv["data"])
                scoring_result["cv_filename"] = cv["filename"]
                scored_results.append(scoring_result)
                progress.update(scoring_task, advance=1)
        
        # Rank results
        ranker = CVRanker()
        ranker.ranked_cvs = sorted(
            scored_results,
            key=lambda x: x.get("final_score", 0),
            reverse=True
        )
        
        # Add ranks
        for idx, cv in enumerate(ranker.ranked_cvs, start=1):
            cv["rank"] = idx
        
        # Calculate metrics
        predicted_ranking = [cv.get("cv_filename") for cv in ranker.ranked_cvs]
        
        # Load ground truth
        gt_manager = get_ground_truth_manager()
        ground_truth = gt_manager.get_ground_truth_ranking()
        relevance_scores = gt_manager.get_relevance_scores()
        
        metrics = {}
        if ground_truth:
            ranking_metrics = get_ranking_metrics()
            tau, tau_p = ranking_metrics.kendall_tau(predicted_ranking, ground_truth)
            rho, rho_p = ranking_metrics.spearman_rho(predicted_ranking, ground_truth)
            
            metrics["kendall_tau"] = round(tau, 4)
            metrics["spearman_rho"] = round(rho, 4)
            
            if relevance_scores:
                ndcg_10 = ranking_metrics.ndcg_at_k(predicted_ranking, relevance_scores, k=10)
                metrics["ndcg@10"] = round(ndcg_10, 4)
        
        # Compile results
        ablation_results = {
            "ablation_name": ablation_name,
            "description": description,
            "config": config.get_all_config(),
            "metrics": metrics,
            "top_10_ranking": [
                {
                    "rank": cv.get("rank"),
                    "filename": cv.get("cv_filename"),
                    "score": round(cv.get("final_score", 0), 4)
                }
                for cv in ranker.ranked_cvs[:10]
            ],
            "score_statistics": {
                "mean": round(sum(cv.get("final_score", 0) for cv in ranker.ranked_cvs) / len(ranker.ranked_cvs), 4),
                "min": round(min(cv.get("final_score", 0) for cv in ranker.ranked_cvs), 4),
                "max": round(max(cv.get("final_score", 0) for cv in ranker.ranked_cvs), 4)
            }
        }
        
        # Save results
        output_path = self.output_dir / f"{ablation_name}_results.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ablation_results, f, indent=2, ensure_ascii=False)
        
        success(f"Saved ablation results to {output_path}")
        
        return ablation_results
    
    def compare_ablations(self, ablation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple ablation results
        
        Args:
            ablation_results: List of ablation result dicts
            
        Returns:
            Comparison report
        """
        comparison = {
            "total_ablations": len(ablation_results),
            "ablations": []
        }
        
        for result in ablation_results:
            comparison["ablations"].append({
                "name": result.get("ablation_name"),
                "description": result.get("description"),
                "metrics": result.get("metrics", {}),
                "mean_score": result.get("score_statistics", {}).get("mean", 0)
            })
        
        # Identify best performing ablation
        if comparison["ablations"]:
            best_ablation = max(
                comparison["ablations"],
                key=lambda x: x.get("metrics", {}).get("kendall_tau", 0)
            )
            comparison["best_ablation"] = best_ablation.get("name")
        
        # Save comparison
        comparison_path = self.output_dir / "ablation_comparison.json"
        with open(comparison_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        
        success(f"Saved ablation comparison to {comparison_path}")
        
        return comparison


def run_all_ablations():
    """Run all predefined ablation studies"""
    
    info("="*60)
    info("RUNNING ABLATION STUDIES")
    info("="*60 + "\n")
    
    # Create ablation configs directory
    ablation_configs_dir = ENV.ABLATION_CONFIGS_DIR
    
    
    runner = AblationRunner()
    
    # Ablation 1: No Publications
    info("Creating Ablation 1: No Publications Weight")
    ablation_1_config = _create_no_publications_config(ablation_configs_dir)
    
    # Ablation 2: Equal Weights
    info("Creating Ablation 2: Equal Weights for All Criteria")
    ablation_2_config = _create_equal_weights_config(ablation_configs_dir)
    
    # Ablation 3: Experience-Heavy
    info("Creating Ablation 3: Experience-Heavy Configuration")
    ablation_3_config = _create_experience_heavy_config(ablation_configs_dir)
    
    
    ablation_results = []
    
    ablation_results.append(runner.run_ablation(
        "ablation_1_no_publications",
        ablation_1_config,
        "Remove publications from scoring (weight=0) to test impact on ranking"
    ))
    
    ablation_results.append(runner.run_ablation(
        "ablation_2_equal_weights",
        ablation_2_config,
        "Use equal weights for all criteria to establish baseline"
    ))
    
    ablation_results.append(runner.run_ablation(
        "ablation_3_experience_heavy",
        ablation_3_config,
        "Prioritize experience over other criteria (weight=0.5)"
    ))
    
   
    comparison = runner.compare_ablations(ablation_results)
    
    
    info("\n" + "="*60)
    info("ABLATION COMPARISON")
    info("="*60)
    
    for abl in comparison["ablations"]:
        info(f"\n{abl['name']}:")
        info(f"  Description: {abl['description']}")
        metrics = abl.get("metrics", {})
        if metrics:
            info(f"  Kendall's Tau: {metrics.get('kendall_tau', 'N/A')}")
            info(f"  Spearman's Rho: {metrics.get('spearman_rho', 'N/A')}")
            info(f"  nDCG@10: {metrics.get('ndcg@10', 'N/A')}")
        info(f"  Mean Score: {abl.get('mean_score', 0):.4f}")
    
    info(f"\nBest Ablation: {comparison.get('best_ablation', 'N/A')}")
    info("="*60 + "\n")
    
    success("All ablation studies completed!")


def _create_no_publications_config(config_dir: Path) -> Path:
    """Create config with publications weight = 0"""
    config = {
        "weights": {
            "education": 0.35,
            "experience": 0.40,
            "publications": 0.0,
            "coherence": 0.15,
            "awards_other": 0.10
        },
        "subweights": {
            "education": {"gpa": 0.5, "degree_level": 0.2, "university_tier": 0.3},
            "experience": {"duration": 0.5, "domain_match": 0.3, "seniority": 0.2},
            "publications": {"if": 0.5, "author_position": 0.3, "venue_quality": 0.2},
            "coherence": {"domain_consistency": 0.6, "progression": 0.4}
        },
        "policies": {
            "missing_values_penalty": 0.10,
            "min_months_experience_for_bonus": 24,
            "experience_bonus": 0.15,
            "first_author_bonus": 0.15,
            "second_author_bonus": 0.05,
            "target_domain": "NLP",
            "domain_match_bonus": 0.20,
            "phd_bonus": 0.20,
            "masters_bonus": 0.10,
            "min_domain_consistency": 0.5
        },
        "normalization": {
            "gpa_scale": 4.0,
            "max_experience_months": 120,
            "max_publications": 10,
            "max_journal_if": 50.0
        }
    }
    
    config_path = config_dir / "ablation_1_no_publications.yaml"
    import yaml
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return config_path


def _create_equal_weights_config(config_dir: Path) -> Path:
    """Create config with equal weights"""
    config = {
        "weights": {
            "education": 0.20,
            "experience": 0.20,
            "publications": 0.20,
            "coherence": 0.20,
            "awards_other": 0.20
        },
        "subweights": {
            "education": {"gpa": 0.5, "degree_level": 0.2, "university_tier": 0.3},
            "experience": {"duration": 0.5, "domain_match": 0.3, "seniority": 0.2},
            "publications": {"if": 0.5, "author_position": 0.3, "venue_quality": 0.2},
            "coherence": {"domain_consistency": 0.6, "progression": 0.4}
        },
        "policies": {
            "missing_values_penalty": 0.10,
            "min_months_experience_for_bonus": 24,
            "experience_bonus": 0.15,
            "first_author_bonus": 0.15,
            "second_author_bonus": 0.05,
            "target_domain": "NLP",
            "domain_match_bonus": 0.20,
            "phd_bonus": 0.20,
            "masters_bonus": 0.10,
            "min_domain_consistency": 0.5
        },
        "normalization": {
            "gpa_scale": 4.0,
            "max_experience_months": 120,
            "max_publications": 10,
            "max_journal_if": 50.0
        }
    }
    
    config_path = config_dir / "ablation_2_equal_weights.yaml"
    import yaml
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return config_path


def _create_experience_heavy_config(config_dir: Path) -> Path:
    """Create config that prioritizes experience"""
    config = {
        "weights": {
            "education": 0.15,
            "experience": 0.50,
            "publications": 0.20,
            "coherence": 0.10,
            "awards_other": 0.05
        },
        "subweights": {
            "education": {"gpa": 0.5, "degree_level": 0.2, "university_tier": 0.3},
            "experience": {"duration": 0.5, "domain_match": 0.3, "seniority": 0.2},
            "publications": {"if": 0.5, "author_position": 0.3, "venue_quality": 0.2},
            "coherence": {"domain_consistency": 0.6, "progression": 0.4}
        },
        "policies": {
            "missing_values_penalty": 0.10,
            "min_months_experience_for_bonus": 24,
            "experience_bonus": 0.15,
            "first_author_bonus": 0.15,
            "second_author_bonus": 0.05,
            "target_domain": "NLP",
            "domain_match_bonus": 0.20,
            "phd_bonus": 0.20,
            "masters_bonus": 0.10,
            "min_domain_consistency": 0.5
        },
        "normalization": {
            "gpa_scale": 4.0,
            "max_experience_months": 120,
            "max_publications": 10,
            "max_journal_if": 50.0
        }
    }
    
    config_path = config_dir / "ablation_3_experience_heavy.yaml"
    import yaml
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return config_path


if __name__ == "__main__":
    run_all_ablations()