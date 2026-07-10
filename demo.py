"""デモ(APIキー不要). `python demo.py`"""
from backend.index import IndexCalculator, AdoptionInput, BenchmarkService, load_formula
from backend.assistant import AssistantApprovalFlow, Citation


def main():
    formula = load_formula()
    calc = IndexCalculator(formula)

    print("=== AI-Adoption Index ===")
    r = calc.compute(AdoptionInput(wau=60, target_users=100, active_departments=4,
                                   total_departments=8, usage_stage_avg=2.1,
                                   governance_checklist_ratio=0.7))
    print(f"  score={r.score:.1f} (version {r.version}) factors={r.as_dict()['factors']}")

    print("\n=== 匿名ベンチマーク(k-匿名性=5) ===")
    bench = BenchmarkService(k_anonymity=formula["k_anonymity"])
    small = bench.segment_benchmark([55, 60, 62], own_score=r.score)
    print(f"  3社セグメント: available={small.available} ({small.reason})")
    big = bench.segment_benchmark([40, 55, 60, 62, 70, 75], own_score=r.score)
    print(f"  6社セグメント: median={big.median} 上位{big.percentile_of}%")

    print("\n=== 顧問承認フロー ===")
    flow = AssistantApprovalFlow()
    d1 = flow.draft("経費精算の締め日は?", "毎月20日です。",
                    [Citation("knowledge", "K-102")])
    print(f"  出典ありドラフト: status={d1.status} (顧問承認前は送信されない: {not flow.is_sent_to_client(d1.id)})")
    flow.approve_and_send(d1.id, advisor="advisor01")
    print(f"  承認後: sent={flow.is_sent_to_client(d1.id)}")
    d2 = flow.draft("来期の売上目標は?", "（不明）", [])
    print(f"  出典なしドラフト: status={d2.status}(創作せず)")


if __name__ == "__main__":
    main()
