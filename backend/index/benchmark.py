"""匿名ベンチマーク(差別化). k-匿名性: 同一セグメント5社未満は非表示."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Dict, List, Optional


@dataclass
class BenchmarkResult:
    available: bool
    reason: str = ""
    n: int = 0
    p25: float = 0.0
    median: float = 0.0
    p75: float = 0.0
    percentile_of: Optional[float] = None   # 対象企業の位置(上位◯%)

    def as_dict(self):
        return self.__dict__


def _quantile(sorted_vals: List[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = q * (len(sorted_vals) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo)


class BenchmarkService:
    def __init__(self, k_anonymity: int = 5) -> None:
        self.k = k_anonymity

    def segment_benchmark(self, segment_scores: List[float],
                          own_score: Optional[float] = None) -> BenchmarkResult:
        n = len(segment_scores)
        if n < self.k:
            return BenchmarkResult(available=False,
                                   reason=f"セグメント企業数 {n} < k={self.k} のため非表示",
                                   n=n)
        s = sorted(segment_scores)
        pct = None
        if own_score is not None:
            # 上位◯%(自社以上のスコア割合)
            higher_or_equal = sum(1 for v in s if v >= own_score)
            pct = round(higher_or_equal / n * 100, 1)
        return BenchmarkResult(available=True, n=n,
                               p25=round(_quantile(s, 0.25), 1),
                               median=round(median(s), 1),
                               p75=round(_quantile(s, 0.75), 1),
                               percentile_of=pct)
