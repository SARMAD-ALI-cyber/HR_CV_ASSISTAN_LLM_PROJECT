import math
from typing import List, Dict, Any, Tuple
from scipy.stats import kendalltau, spearmanr
import numpy as np

class RankingMetrics:
    """Calculate ranking quality metrics"""
    
    def __init__(self):
        pass
    
    def kendall_tau(
        self, 
        predicted_ranking: List[str], 
        ground_truth_ranking: List[str]
    ) -> Tuple[float, float]:
        """
        Calculate Kendall's Tau correlation
        
        Args:
            predicted_ranking: List of CV filenames in predicted order
            ground_truth_ranking: List of CV filenames in ground truth order
            
        Returns:
            Tuple of (tau, p_value)
        """
        
        pred_ranks = self._convert_to_ranks(predicted_ranking, ground_truth_ranking)
        true_ranks = list(range(1, len(ground_truth_ranking) + 1))
        
        if len(pred_ranks) < 2:
            return 0.0, 1.0
        
        tau, p_value = kendalltau(pred_ranks, true_ranks)
        return tau, p_value
    
    def spearman_rho(
        self,
        predicted_ranking: List[str],
        ground_truth_ranking: List[str]
    ) -> Tuple[float, float]:
        """
        Calculate Spearman's Rho correlation
        
        Args:
            predicted_ranking: List of CV filenames in predicted order
            ground_truth_ranking: List of CV filenames in ground truth order
            
        Returns:
            Tuple of (rho, p_value)
        """
       
        pred_ranks = self._convert_to_ranks(predicted_ranking, ground_truth_ranking)
        true_ranks = list(range(1, len(ground_truth_ranking) + 1))
        
        if len(pred_ranks) < 2:
            return 0.0, 1.0
        
        rho, p_value = spearmanr(pred_ranks, true_ranks)
        return rho, p_value
    
    def ndcg_at_k(
        self,
        predicted_ranking: List[str],
        relevance_scores: Dict[str, float],
        k: int = 10
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain at K
        
        Args:
            predicted_ranking: List of CV filenames in predicted order
            relevance_scores: Dict mapping CV filename to relevance score
            k: Top K positions to consider
            
        Returns:
            nDCG@k score (0-1)
        """
        
        top_k_pred = predicted_ranking[:k]
        
        
        dcg = 0.0
        for i, cv_id in enumerate(top_k_pred, start=1):
            relevance = relevance_scores.get(cv_id, 0.0)
            dcg += relevance / math.log2(i + 1)
        
        
        sorted_relevances = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg = 0.0
        for i, relevance in enumerate(sorted_relevances, start=1):
            idcg += relevance / math.log2(i + 1)
        
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def mean_average_precision(
        self,
        predicted_ranking: List[str],
        relevant_items: List[str]
    ) -> float:
        """
        Calculate Mean Average Precision
        
        Args:
            predicted_ranking: List of CV filenames in predicted order
            relevant_items: List of relevant CV filenames
            
        Returns:
            MAP score (0-1)
        """
        if not relevant_items:
            return 0.0
        
        relevant_set = set(relevant_items)
        num_relevant = len(relevant_set)
        
        precision_sum = 0.0
        num_relevant_found = 0
        
        for i, cv_id in enumerate(predicted_ranking, start=1):
            if cv_id in relevant_set:
                num_relevant_found += 1
                precision_at_i = num_relevant_found / i
                precision_sum += precision_at_i
        
        if num_relevant_found == 0:
            return 0.0
        
        return precision_sum / num_relevant
    
    def _convert_to_ranks(
        self,
        predicted_ranking: List[str],
        ground_truth_ranking: List[str]
    ) -> List[int]:
        """
        Convert predicted ranking to numeric ranks based on ground truth
        
        Args:
            predicted_ranking: Predicted order
            ground_truth_ranking: Ground truth order
            
        Returns:
            List of ranks for predicted items in ground truth order
        """
        
        ground_truth_map = {cv_id: rank for rank, cv_id in enumerate(ground_truth_ranking, start=1)}
        
        
        pred_ranks = []
        for cv_id in predicted_ranking:
            if cv_id in ground_truth_map:
                pred_ranks.append(ground_truth_map[cv_id])
        
        return pred_ranks
    
    def calculate_all_metrics(
        self,
        predicted_ranking: List[str],
        ground_truth_ranking: List[str] = None,
        relevance_scores: Dict[str, float] = None,
        k_values: List[int] = [5, 10, 20]
    ) -> Dict[str, Any]:
        """
        Calculate all ranking metrics
        
        Args:
            predicted_ranking: Predicted ranking
            ground_truth_ranking: Ground truth ranking (optional)
            relevance_scores: Relevance scores for nDCG (optional)
            k_values: K values for nDCG@k
            
        Returns:
            Dict with all metrics
        """
        metrics = {}
        
       
        if ground_truth_ranking:
            tau, tau_p = self.kendall_tau(predicted_ranking, ground_truth_ranking)
            rho, rho_p = self.spearman_rho(predicted_ranking, ground_truth_ranking)
            
            metrics["kendall_tau"] = {
                "value": round(tau, 4),
                "p_value": round(tau_p, 4),
                "significant": bool(tau_p < 0.05)
            }
            
            metrics["spearman_rho"] = {
                "value": round(rho, 4),
                "p_value": round(rho_p, 4),
                "significant": bool(rho_p < 0.05)
            }
        
        
        if relevance_scores:
            metrics["ndcg"] = {}
            for k in k_values:
                ndcg_k = self.ndcg_at_k(predicted_ranking, relevance_scores, k)
                metrics["ndcg"][f"ndcg@{k}"] = round(ndcg_k, 4)
        
        return metrics


class PairwiseMetrics:
    """Calculate pairwise comparison metrics"""
    
    def __init__(self):
        pass
    
    def pairwise_accuracy(
        self,
        predicted_ranking: List[str],
        ground_truth_pairs: List[Tuple[str, str]]
    ) -> float:
        """
        Calculate pairwise accuracy
        
        Args:
            predicted_ranking: Predicted ranking (ordered list)
            ground_truth_pairs: List of (better_cv, worse_cv) tuples
            
        Returns:
            Accuracy (0-1)
        """
        if not ground_truth_pairs:
            return 0.0
        
        
        rank_map = {cv_id: rank for rank, cv_id in enumerate(predicted_ranking)}
        
        correct = 0
        total = len(ground_truth_pairs)
        
        for better_cv, worse_cv in ground_truth_pairs:
            
            if better_cv in rank_map and worse_cv in rank_map:
                
                if rank_map[better_cv] < rank_map[worse_cv]:  # Lower rank = better
                    correct += 1
        
        return correct / total if total > 0 else 0.0
    
    def generate_all_pairs(self, ranking: List[str]) -> List[Tuple[str, str]]:
        """
        Generate all pairwise comparisons from ranking
        
        Args:
            ranking: Ordered list of CV IDs
            
        Returns:
            List of (better_cv, worse_cv) pairs
        """
        pairs = []
        for i in range(len(ranking)):
            for j in range(i + 1, len(ranking)):
                pairs.append((ranking[i], ranking[j]))
        return pairs
    
    def pairwise_agreement_rate(
        self,
        ranking_a: List[str],
        ranking_b: List[str]
    ) -> float:
        """
        Calculate agreement rate between two rankings
        
        Args:
            ranking_a: First ranking
            ranking_b: Second ranking
            
        Returns:
            Agreement rate (0-1)
        """
        
        pairs_a = self.generate_all_pairs(ranking_a)
        
       
        return self.pairwise_accuracy(ranking_b, pairs_a)


class FaithfulnessMetrics:
    """Metrics for explanation faithfulness"""
    
    def __init__(self):
        pass
    
    def evidence_match_rate(
        self,
        explanations: List[Dict[str, Any]],
        cv_data: Dict[str, Dict[str, Any]]
    ) -> float:
        """
        Calculate how often explanations reference actual CV content
        
        Args:
            explanations: List of explanation objects
            cv_data: Dict mapping CV ID to CV data
            
        Returns:
            Match rate (0-1)
        """
        if not explanations:
            return 0.0
        
        total_reasons = 0
        matched_reasons = 0
        
        for explanation in explanations:
            reasons = explanation.get("top_reasons", [])
            
            for reason in reasons:
                total_reasons += 1
                
               
                evidence = reason.get("evidence", {})
                if evidence and (evidence.get("cv_a") or evidence.get("cv_b")):
                    matched_reasons += 1
        
        return matched_reasons / total_reasons if total_reasons > 0 else 0.0
    
    def counterfactual_sensitivity(
        self,
        original_ranking: List[Tuple[str, float]],
        modified_ranking: List[Tuple[str, float]],
        weight_change: float
    ) -> Dict[str, Any]:
        """
        Test if ranking changes appropriately when weights change
        
        Args:
            original_ranking: List of (cv_id, score) tuples
            modified_ranking: List of (cv_id, score) after weight change
            weight_change: Magnitude of weight change
            
        Returns:
            Sensitivity metrics
        """
    
        original_ranks = {cv_id: rank for rank, (cv_id, _) in enumerate(original_ranking, start=1)}
        modified_ranks = {cv_id: rank for rank, (cv_id, _) in enumerate(modified_ranking, start=1)}
        
        rank_changes = []
        score_changes = []
        
        original_scores = {cv_id: score for cv_id, score in original_ranking}
        modified_scores = {cv_id: score for cv_id, score in modified_ranking}
        
        for cv_id in original_ranks.keys():
            if cv_id in modified_ranks:
                rank_change = abs(original_ranks[cv_id] - modified_ranks[cv_id])
                rank_changes.append(rank_change)
                
                score_change = abs(original_scores[cv_id] - modified_scores[cv_id])
                score_changes.append(score_change)
        
        return {
            "mean_rank_change": round(np.mean(rank_changes), 2) if rank_changes else 0,
            "max_rank_change": int(max(rank_changes)) if rank_changes else 0,
            "mean_score_change": round(np.mean(score_changes), 4) if score_changes else 0,
            "weight_change": weight_change,
            "sensitive": np.mean(rank_changes) > 0.5 if rank_changes else False
        }



_ranking_metrics = None
_pairwise_metrics = None
_faithfulness_metrics = None

def get_ranking_metrics() -> RankingMetrics:
    global _ranking_metrics
    if _ranking_metrics is None:
        _ranking_metrics = RankingMetrics()
    return _ranking_metrics

def get_pairwise_metrics() -> PairwiseMetrics:
    global _pairwise_metrics
    if _pairwise_metrics is None:
        _pairwise_metrics = PairwiseMetrics()
    return _pairwise_metrics

def get_faithfulness_metrics() -> FaithfulnessMetrics:
    global _faithfulness_metrics
    if _faithfulness_metrics is None:
        _faithfulness_metrics = FaithfulnessMetrics()
    return _faithfulness_metrics