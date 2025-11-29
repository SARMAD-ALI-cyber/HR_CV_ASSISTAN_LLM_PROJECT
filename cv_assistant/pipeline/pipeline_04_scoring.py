import json
from pathlib import Path
from typing import List, Dict, Any
from cv_assistant import ENV
from cv_assistant.scoring import get_aggregator
from cv_assistant.config import get_config
from cv_assistant.utils.logger import info, success, error, warn
from cv_assistant.utils.status import get_progress_bar

def load_cv_json(json_path: Path) -> Dict[str, Any]:
    """Load CV data from JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_scored_cv(scored_data: Dict[str, Any], output_path: Path):
    """Save scored CV data to JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scored_data, f, indent=2, ensure_ascii=False)

def PIPELINE_04_SCORING(json_dir: Path = None, output_dir: Path = None) -> List[Dict[str, Any]]:
    """
    Score all CVs from extracted JSON files
    
    Args:
        json_dir: Directory containing extracted CV JSONs (default: ENV.JSON_DIR)
        output_dir: Directory to save scored CVs (default: ENV.OUTPUT_DIR / "scored_cvs")
        
    Returns:
        List of all scored CV results
    """
    # Set default directories
    if json_dir is None:
        json_dir = ENV.JSON_DIR
    
    if output_dir is None:
        output_dir = ENV.SCORED_CV_DIR
    
    # Get list of CV JSON files
    cv_json_files = list(json_dir.glob("*.json"))
    
    if not cv_json_files:
        warn(f"No CV JSON files found in {json_dir}")
        return []
    
    info(f"Found {len(cv_json_files)} CV JSON files to score")
    
    # Initialize aggregator
    aggregator = get_aggregator()
    config = get_config()
    
    info(f"Using config: target_domain = {config.get_policy('target_domain')}")
    
    all_scored_results = []
    
    with get_progress_bar() as progress:
        scoring_task = progress.add_task(
            description=f"[cyan]Scoring {len(cv_json_files)} CVs...",
            total=len(cv_json_files)
        )
        
        for json_file in cv_json_files:
            try:
                # Load CV data
                cv_data = load_cv_json(json_file)
                
                # Calculate scores
                scoring_results = aggregator.calculate_final_score(cv_data)
                
                # Add metadata
                scoring_results["cv_filename"] = json_file.stem
                scoring_results["cv_path"] = str(json_file)
                
                # Combine original CV data with scoring results
                scored_cv = {
                    "metadata": {
                        "filename": json_file.stem,
                        "original_json_path": str(json_file)
                    },
                    "cv_data": cv_data,
                    "scoring_results": scoring_results
                }
                
                # Save individual scored CV
                output_path = output_dir / f"{json_file.stem}_scored.json"
                save_scored_cv(scored_cv, output_path)
                
                # Add to results list
                all_scored_results.append(scoring_results)
                
                success(f"Scored {json_file.stem}: {scoring_results['final_score_percentage']}%")
                
            except Exception as e:
                error(f"Error scoring {json_file.stem}: {str(e)}")
                continue
            
            progress.update(scoring_task, advance=1)
    
    # Save summary of all scores
    summary_path = ENV.OUTPUT_DIR / "scoring_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            "total_cvs_scored": len(all_scored_results),
            "config_used": config.get_all_config(),
            "scores": all_scored_results
        }, f, indent=2, ensure_ascii=False)
    
    success(f"Saved scoring summary to {summary_path}")
    
    return all_scored_results


if __name__ == "__main__":
    # Run scoring pipeline
    results = PIPELINE_04_SCORING()
    info(f"Successfully scored {len(results)} CVs")