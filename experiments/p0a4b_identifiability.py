from __future__ import annotations

import argparse, json
from pathlib import Path
import numpy as np
from icq_ra import estimate_icq_ra

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def edges(c):
    return np.linspace(c["histogram_min"], c["histogram_max"], c["histogram_bins"] + 1)

def make(name, seed, c, g):
    n = c["n_per_seed"]
    r = np.random.default_rng(seed)
    h = r.integers(0, 2, n)
    u = r.choice(np.asarray(c["intervention_values"], float), n)
    e = r.normal(0.0, c["noise_sigma"], n)
    a, gh = c["intervention_main_effect"], c["history_effect"]

    if name == "OBSERVED_HU_INTERACTION":
        q = r.integers(0, 2, n)
        k = g["alternative_classes"][name]["interaction_strength"]
        y = a*u + gh*h + k*h*u + e
    elif name == "HIDDEN_MODIFIER_PROXY":
        z = r.integers(0, 2, n)
        p = g["alternative_classes"][name]["q_proxy_flip_probability"]
        q = np.where(r.random(n) < p, 1-z, z)
        k = g["alternative_classes"][name]["hidden_modifier_strength"]
        y = a*u + gh*h + k*z*u + e
    else:
        raise ValueError(name)
    return q, h, u, y

def run(name, seed, c, g):
    q,h,u,y = make(name, seed, c, g)
    est = estimate_icq_ra(
        q,h,u,y,
        intervention_values=c["intervention_values"],
        history_values=c["history_values"],
        bin_edges=edges(c),
        min_cell=c["min_cell"],
        n_permutations=c["n_permutations"],
        seed=seed + c["estimator_seed_offset"],
    )
    return {"seed":seed, "icq_ra":float(est.value), "finite":bool(np.isfinite(est.value))}

def stats(v):
    x=np.asarray(v,float)
    return {
        "n":int(x.size),"mean":float(x.mean()),"std":float(x.std(ddof=1)),
        "median":float(np.median(x)),"min":float(x.min()),"max":float(x.max())
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--phase0a-config",required=True)
    p.add_argument("--p0a4b-config",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    c,g=load(a.phase0a_config),load(a.p0a4b_config)
    seeds=[int(s) for s in g["seeds"]]
    forbidden=set(range(1101,1131))|set(range(2101,2131))|set(range(3101,3161))
    pre={
        "seed_bank_disjoint":not bool(set(seeds)&forbidden),
        "run_count_exact":len(seeds)==g["expected_runs_per_alternative"],
        "seeds_unique":len(seeds)==len(set(seeds))
    }
    if not all(pre.values()):
        out={"protocol_id":g["protocol_id"],"execution_status":"STOP_PREFLIGHT","scientific_decision":"INCONCLUSIVE","preflight":pre}
        Path(a.out).parent.mkdir(parents=True,exist_ok=True)
        Path(a.out).write_text(json.dumps(out,indent=2),encoding="utf-8")
        print(json.dumps(out,indent=2)); raise SystemExit(1)

    threshold=float(g["active_criterion_mean_icq_ra_min"])
    results={}; hit=False; valid=True
    for name in g["alternative_classes"]:
        rows=[run(name,s,c,g) for s in seeds]
        sm=stats([x["icq_ra"] for x in rows])
        ok=all(x["finite"] for x in rows)
        reaches=sm["mean"]>=threshold
        hit=hit or reaches; valid=valid and ok
        results[name]={"dag":g["alternative_classes"][name]["dag"],"summary_icq_ra":sm,"reaches_frozen_active_criterion":reaches,"all_finite":ok,"rows":rows}

    decision="INCONCLUSIVE" if not valid else ("FAIL_NONIDENTIFIABLE" if hit else "SURVIVED_DECLARED_ALTERNATIVES")
    out={
        "protocol_id":g["protocol_id"],"gate":g["gate"],"execution_status":"COMPLETE",
        "scientific_decision":decision,"preflight":pre,
        "frozen_active_criterion_mean_icq_ra_min":threshold,"results":results,
        "interpretation":g["claim_if_failed"] if decision=="FAIL_NONIDENTIFIABLE" else g["claim_ceiling_if_survived"],
        "phase0a_overall_qualification_authorized":False,"qualia_claim_authorized":False
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k!="results"}|{"model_summaries":{k:v["summary_icq_ra"]|{"reaches":v["reaches_frozen_active_criterion"]} for k,v in results.items()}},indent=2))

if __name__=="__main__":
    main()
