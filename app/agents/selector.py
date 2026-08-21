from typing import List, Optional
from app.models.candidate import AlgorithmCandidate

class SelectorAgent:
    """Archaeological Selector: Identifies non-dominated winners and optimal trade-offs."""

    def select_champion(self, candidates: List[AlgorithmCandidate]) -> Optional[AlgorithmCandidate]:
        if not candidates:
            return None

        # Filter strictly correct candidates first
        correct_candidates = [c for c in candidates if c.passed_correctness or c.accuracy_percentage >= 99.9]
        pool = correct_candidates if correct_candidates else candidates

        # Pick candidate with highest composite score on the Pareto frontier
        champion = max(pool, key=lambda c: (1 if c.is_pareto_optimal else 0, c.pareto_composite_score))
        
        for c in candidates:
            c.is_winner = (c.id == champion.id)

        return champion

selector_agent = SelectorAgent()
