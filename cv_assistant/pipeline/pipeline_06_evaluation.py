import json
from pathlib import Path
from cv_assistant import ENV
from cv_assistant.evaluation import (
    get_ranking_metrics,
    get_pairwise_metrics,
    get_faithfulness_metrics,
    get_ground_truth_manager
)
from cv_assistant.utils.logger import info, success, warn

def PIPELINE_06_EVALUATION(
    ranked_file: Path = None,
    explanations_dir: Path = None,
    output_dir: Path = None,
    create_sample_ground_truth: bool = True
):
    """
    Evaluate ranking quality with multiple metrics
    
    Args:
        ranked_file: Path to ranked_candidates.json
        explanations_dir: Path to explanations directory
        output_dir: Output directory for evaluation results
        create_sample_ground_truth: Whether to create sample ground truth
    """
   
    if ranked_file is None:
        ranked_file = ENV.RANKING_DIR / "ranked_candidates.json"
    
    if explanations_dir is None:
        explanations_dir = ENV.EXPANATIONS_DIR
    
    if output_dir is None:
        output_dir = ENV.EVALUATION_DIR
        
    
    if not ranked_file.exists():
        warn(f"Ranked candidates file not found: {ranked_file}")
        return
    
    info("Starting evaluation pipeline...")
    
   
    with open(ranked_file, 'r', encoding='utf-8') as f:
        ranked_data = json.load(f)
    
    ranked_cvs = ranked_data.get("ranked_candidates", [])
    predicted_ranking = [cv.get("cv_filename") for cv in ranked_cvs]
    
    info(f"Loaded {len(predicted_ranking)} ranked CVs")
    
    
    ranking_metrics = get_ranking_metrics()
    pairwise_metrics = get_pairwise_metrics()
    faithfulness_metrics = get_faithfulness_metrics()
    gt_manager = get_ground_truth_manager()
    
   
    if create_sample_ground_truth:
        info("Creating sample ground truth annotations...")
        gt_manager.create_sample_ground_truth(ranked_cvs, sample_size=20)
        gt_manager.create_sample_pairwise_preferences(ranked_cvs, num_pairs=50)
        success("Created sample ground truth")
    
   
    ground_truth_ranking = gt_manager.get_ground_truth_ranking()
    pairwise_preferences = gt_manager.load_pairwise_preferences()
    relevance_scores = gt_manager.get_relevance_scores()
    
    
    evaluation_results = {
        "total_cvs": len(predicted_ranking),
        "evaluation_date": _get_timestamp(),
        "metrics": {}
    }
    
    # 1. Ranking Correlation Metrics
    if ground_truth_ranking:
        info("Calculating Kendall's Tau and Spearman's Rho...")
        correlation_metrics = ranking_metrics.calculate_all_metrics(
            predicted_ranking,
            ground_truth_ranking,
            relevance_scores,
            k_values=[5, 10, 20]
        )
        evaluation_results["metrics"]["correlation"] = correlation_metrics
        
        info(f"  Kendall's Tau: {correlation_metrics.get('kendall_tau', {}).get('value', 0):.4f}")
        info(f"  Spearman's Rho: {correlation_metrics.get('spearman_rho', {}).get('value', 0):.4f}")
    
    # 2. Pairwise Accuracy
    if pairwise_preferences:
        info("Calculating pairwise accuracy...")
        pairwise_acc = pairwise_metrics.pairwise_accuracy(
            predicted_ranking,
            pairwise_preferences
        )
        evaluation_results["metrics"]["pairwise_accuracy"] = {
            "value": round(pairwise_acc, 4),
            "total_pairs": len(pairwise_preferences)
        }
        info(f"  Pairwise Accuracy: {pairwise_acc:.4f}")
    
    # 3. nDCG@k
    if relevance_scores:
        info("Calculating nDCG@k...")
        for k in [5, 10, 20]:
            ndcg_k = ranking_metrics.ndcg_at_k(predicted_ranking, relevance_scores, k)
            if "ndcg" not in evaluation_results["metrics"]:
                evaluation_results["metrics"]["ndcg"] = {}
            evaluation_results["metrics"]["ndcg"][f"ndcg@{k}"] = round(ndcg_k, 4)
            info(f"  nDCG@{k}: {ndcg_k:.4f}")
    
    # 4. Explanation Faithfulness
    if explanations_dir.exists():
        info("Calculating explanation faithfulness...")
        explanations = _load_explanations(explanations_dir)
        
        if explanations:
            evidence_match = faithfulness_metrics.evidence_match_rate(
                explanations,
                {}  # Would pass CV data in production
            )
            evaluation_results["metrics"]["faithfulness"] = {
                "evidence_match_rate": round(evidence_match, 4),
                "total_explanations": len(explanations)
            }
            info(f"  Evidence Match Rate: {evidence_match:.4f}")
    
    # 5. Score Distribution Analysis
    info("Analyzing score distribution...")
    scores = [cv.get("final_score", 0) for cv in ranked_cvs]
    evaluation_results["score_distribution"] = {
        "mean": round(sum(scores) / len(scores), 4) if scores else 0,
        "std": round(_calculate_std(scores), 4) if scores else 0,
        "min": round(min(scores), 4) if scores else 0,
        "max": round(max(scores), 4) if scores else 0,
        "quartiles": {
            "q1": round(_percentile(scores, 25), 4) if scores else 0,
            "q2": round(_percentile(scores, 50), 4) if scores else 0,
            "q3": round(_percentile(scores, 75), 4) if scores else 0
        }
    }
    
    # Save evaluation results
    output_path = output_dir / "evaluation_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_results, f, indent=2, ensure_ascii=False)
    
    success(f"Saved evaluation results to {output_path}")
    
    
    info("\n" + "="*60)
    info("EVALUATION SUMMARY")
    info("="*60)
    
    if "correlation" in evaluation_results["metrics"]:
        corr = evaluation_results["metrics"]["correlation"]
        info(f"Kendall's Tau:      {corr.get('kendall_tau', {}).get('value', 0):.4f}")
        info(f"Spearman's Rho:     {corr.get('spearman_rho', {}).get('value', 0):.4f}")
    
    if "pairwise_accuracy" in evaluation_results["metrics"]:
        pw = evaluation_results["metrics"]["pairwise_accuracy"]
        info(f"Pairwise Accuracy:  {pw.get('value', 0):.4f}")
    
    if "ndcg" in evaluation_results["metrics"]:
        ndcg = evaluation_results["metrics"]["ndcg"]
        info(f"nDCG@5:            {ndcg.get('ndcg@5', 0):.4f}")
        info(f"nDCG@10:           {ndcg.get('ndcg@10', 0):.4f}")
    
    if "faithfulness" in evaluation_results["metrics"]:
        faith = evaluation_results["metrics"]["faithfulness"]
        info(f"Evidence Match:     {faith.get('evidence_match_rate', 0):.4f}")
    
    info("="*60 + "\n")
    
    return evaluation_results


def _load_explanations(explanations_dir: Path) -> list:
    """Load all explanation JSON files"""
    explanations = []
    for exp_file in explanations_dir.glob("*.json"):
        with open(exp_file, 'r', encoding='utf-8') as f:
            explanations.append(json.load(f))
    return explanations


def _get_timestamp() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _calculate_std(values: list) -> float:
    """Calculate standard deviation"""
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5


def _percentile(values: list, percentile: float) -> float:
    """Calculate percentile"""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    k = (len(sorted_values) - 1) * (percentile / 100)
    f = int(k)
    c = k - f
    if f + 1 < len(sorted_values):
        return sorted_values[f] + c * (sorted_values[f + 1] - sorted_values[f])
    return sorted_values[f]


if __name__ == "__main__":
    PIPELINE_06_EVALUATION()