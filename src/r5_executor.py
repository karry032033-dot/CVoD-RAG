"""R5 executor with per-consumer S/T fallbacks over shared physical responses."""
import hashlib
from r2_executor import ARMS, SAMPLE_FIELDS, lexical_trigger
from r2_adapter import identity
from r4_policy import apply_s_fallback
from r5_policy import apply_t_fallback


def execute_arm(sample, invoke, factory, arm, *, decisions):
    use_l, use_s, use_t = ARMS[arm]
    public = {k: sample[k] for k in SAMPLE_FIELDS}
    sid, q, c, y0 = (public[k] for k in SAMPLE_FIELDS)
    requests, t_decisions, t_outcomes = [], [], []
    physical_t_attempted = False
    logical_t_attempted = False

    def t_candidate(stage, pre_t):
        nonlocal physical_t_attempted, logical_t_attempted
        req = factory("T", public)
        req["realization_id"] += ":level0"
        result = invoke(req)
        requests.append(req)
        key, _ = identity(req)
        physical_t_attempted = True
        logical = stage == "terminal_T"
        logical_t_attempted = logical_t_attempted or logical
        verified = result.get("state") == "SUCCESS" or result.get("r5_provenance_verified") is True
        decision = apply_t_fallback(sample_id=sid, arm_id=arm, stage=stage,
            pre_t_answer=pre_t, request_key=key, response=result,
            expected_model=req["model"], verified=verified,
            logical_t_module_attempted=logical)
        t_outcomes.append(decision)
        if decision["t_fallback_applied"]:
            t_decisions.append(decision)
            decisions.append(decision)
        return decision["final_selected_answer"]

    l_fired = bool(use_l and lexical_trigger(q, y0, c))
    current = t_candidate("L_candidate", y0) if l_fired else y0
    s_fired, s_decision = False, None
    if use_s:
        dreq = factory("D", public, current)
        dres = invoke(dreq)
        requests.append(dreq)
        if dres.get("state") != "SUCCESS" or not dres.get("answer"):
            raise RuntimeError(f"{sid}/{arm}: incomplete D: {dres.get('state')} {dres.get('reason')}")
        if str(dres.get("response_text", dres["answer"])).strip() == "OFF_TOPIC":
            s_fired = True
            rreq = factory("R", public)
            rres = invoke(rreq)
            requests.append(rreq)
            if rres.get("state") == "SUCCESS" and rres.get("answer"):
                current = rres["answer"]
            else:
                key, _ = identity(rreq)
                s_decision = apply_s_fallback({"sample_id": sid, "arm_id": arm,
                    "s_trigger": True, "pre_s_answer": current,
                    "failed_request_key": key,
                    "cost_provenance": {k: rres.get(k) for k in
                        ("prompt_tokens", "generated_tokens", "elapsed_seconds")}},
                    rres, expected_model=rreq["model"],
                    verified=bool(rres.get("r5_provenance_verified") or rres.get("r4_provenance_verified")))
                s_decision["raw_response_sha256"] = hashlib.sha256(rres["raw"].encode("utf-8")).hexdigest()
                s_decision["failure_action"] = "R"
                current = s_decision["final_answer"]
                decisions.append(s_decision)
    if use_t and not s_fired and not l_fired:
        current = t_candidate("terminal_T", current)
    return {"answer": current, "requests": requests, "l_trigger": l_fired,
            "s_trigger": s_fired, "s_fallback": s_decision, "t_fallbacks": t_decisions,
            "t_outcomes": t_outcomes,
            "physical_t_candidate_attempted": physical_t_attempted,
            "logical_t_module_attempted": logical_t_attempted,
            "actual_t_stages": [x["stage"] for x in t_outcomes]}


def execute_sample(sample, invoke, factory, *, decisions):
    traces = {arm: execute_arm(sample, invoke, factory, arm, decisions=decisions) for arm in ARMS}
    return {"sample_id": sample["sample_id"],
            "outputs": {arm: trace["answer"] for arm, trace in traces.items()},
            "traces": traces}


def execute(samples, invoke, factory, on_sample=None, decisions=None):
    decisions = [] if decisions is None else decisions
    ids = [x["sample_id"] for x in samples]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate sample IDs")
    responses = {}

    def dedup(request):
        key, _ = identity(request)
        if key not in responses:
            responses[key] = invoke(request)
        return responses[key]

    rows = []
    for sample in samples:
        row = execute_sample(sample, dedup, factory, decisions=decisions)
        rows.append(row)
        if on_sample:
            on_sample(row)
    return rows
