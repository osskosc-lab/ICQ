import json
from pathlib import Path

def test_p0a4_seed_banks_are_disjoint():
    a=json.loads(Path("configs/p0a4a_null_family_audit.json").read_text())
    b=json.loads(Path("configs/p0a4b_identifiability.json").read_text())
    sa=set(a["paired_seeds"]); sb=set(b["seeds"])
    old=set(range(1101,1131))|set(range(2101,2131))
    assert len(sa)==60 and len(sb)==30
    assert not (sa & old)
    assert not (sb & old)
    assert not (sa & sb)

def test_p0a4b_models_declare_no_direct_q_path():
    b=json.loads(Path("configs/p0a4b_identifiability.json").read_text())
    assert all("Q -/-> Y" in m["dag"] for m in b["alternative_classes"].values())
