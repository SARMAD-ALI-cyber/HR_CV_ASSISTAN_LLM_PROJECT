import json
from pathlib import Path
from cv_assistant import ENV
from cv_assistant.ranking import get_ranker
from cv_assistant.explanations import get_explanation_generator
from cv_assistant.utils.logger import info, success, warn
from cv_assistant.utils.status import get_progress_bar

def PIPELINE_05_RANKING(
    number_of_candidates_to_Rank,
    summary_path: Path = None,
    output_dir: Path = None,
    generate_explanations: bool = True,
    
):
    """
    Rank CVs and generate explanations
    
    Args:
        summary_path: Path to scoring_summary.json
        output_dir: Output directory for ranked results
        generate_explanations: Whether to generate A vs B explanations
    """
  
    if summary_path is None:
        summary_path = ENV.OUTPUT_DIR / "scoring_summary.json"
    
    if output_dir is None:
        output_dir = ENV.RANKING_DIR
        output_dir.mkdir(exist_ok=True, parents=True)
    
    if not summary_path.exists():
        warn(f"Scoring summary not found: {summary_path}")
        return
    
    info("Starting ranking pipeline...")
    

    ranker = get_ranker()
    
 
    info("Ranking CVs by score...")
    ranked_cvs = ranker.rank_from_summary(summary_path)
    
    info(f"Ranked {len(ranked_cvs)} CVs")
    
  
    ranked_output_path = output_dir / "ranked_candidates.json"
    ranker.save_ranked_list(ranked_output_path)
    success(f"Saved ranked list to {ranked_output_path}")
    
    
    report = ranker.generate_ranking_report(number_of_candidates_to_Rank)
    report_path = output_dir / "ranking_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    success(f"Saved ranking report to {report_path}")
    

    info("\n" + "="*60)
    info(f"TOP {number_of_candidates_to_Rank} CANDIDATES")
    info("="*60)
    for cv in ranked_cvs[:number_of_candidates_to_Rank]:
        rank = cv.get("rank")
        filename = cv.get("cv_filename")
        score = cv.get("final_score_percentage", 0)
        info(f"Rank {rank:2d}: {filename:20s} - Score: {score:.2f}%")
    info("="*60 + "\n")
    
  
    if generate_explanations:
        info("Generating explanations for top candidate comparisons...")
        explanations_dir = ENV.EXPANATIONS_DIR
        
        
        explanation_gen = get_explanation_generator()
        
    
        num_explanations = min(number_of_candidates_to_Rank, len(ranked_cvs) - 1)
        
        with get_progress_bar() as progress:
            explanation_task = progress.add_task(
                description="[green]Generating explanations...",
                total=num_explanations
            )
            
            for i in range(num_explanations):
                cv_a = ranked_cvs[i]
                cv_b = ranked_cvs[i + 1]
                
                
                explanation = explanation_gen.explain_why_a_better_than_b(
                    cv_a, cv_b, include_evidence=True
                )
                
              
                filename_a = cv_a.get("cv_filename")
                filename_b = cv_b.get("cv_filename")
                explanation_path = explanations_dir / f"rank{i+1}_vs_rank{i+2}_{filename_a}_vs_{filename_b}.json"
                
                with open(explanation_path, 'w', encoding='utf-8') as f:
                    json.dump(explanation, f, indent=2, ensure_ascii=False)
                
                progress.update(explanation_task, advance=1)
        
        success(f"Generated {num_explanations} explanations in {explanations_dir}")
        
        # Also generate explanation for rank 1 vs rank number_of_candidates_to_Rank (if available)
        if len(ranked_cvs) >= number_of_candidates_to_Rank:
            cv_1 = ranked_cvs[0]
            cv_last = ranked_cvs[number_of_candidates_to_Rank-1]
            
            explanation = explanation_gen.explain_why_a_better_than_b(
                cv_1, cv_last, include_evidence=True
            )
            
            explanation_path = explanations_dir / f"rank1_vs_rank{number_of_candidates_to_Rank}_detailed.json"
            with open(explanation_path, 'w', encoding='utf-8') as f:
                json.dump(explanation, f, indent=2, ensure_ascii=False)
            
            success(f"Generated detailed comparison: Rank 1 vs Rank {number_of_candidates_to_Rank}")
    
    info("Ranking pipeline completed successfully!")
    
    return ranked_cvs


if __name__ == "__main__":
    PIPELINE_05_RANKING(15)