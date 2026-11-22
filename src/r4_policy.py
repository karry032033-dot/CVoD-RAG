"""P2-R4 deterministic S fallback. This module never sends model requests."""
import json

from r2_adapter import clean_answer

PROTOCOL_VERSION = "P2-R4-S-FALLBACK-v1"


def select_s_answer(pre_s, response, *, expected_model, verified=False, s_triggered=True):
    """Return (answer, state, reason); only verified completed S failures may fallback."""
    if not s_triggered:
        return pre_s, "NOT_TRIGGERED", None
    if not verified:
        raise RuntimeError("S failure provenance is unverified")
    raw = response.get("raw")
    if response.get("state") not in ("SUCCESS", "FAILED", "TRUNCATED"):
        raise RuntimeError("S response state is not eligible for fallback")
    try:
        data = json.loads(raw) if isinstance(raw, str) else None
    except (ValueError, TypeError):
        data = None
    # State labels alone are insufficient. Check the original completion envelope.
    if (response.get("http_status") != 200 or not isinstance(data, dict)
            or data.get("model") != expected_model
            or data.get("done") is not True or data.get("done_reason") not in ("stop", "length")
            or not isinstance(data.get("response"), str)):
        raise RuntimeError("S failure is not a verified completed model response")
    if data["done_reason"] == "length":
        reason = "done_reason_length"
    elif not clean_answer(data["response"]):
        reason = "empty_extracted_answer"
    else:
        return clean_answer(data["response"]), "SUCCESS", None
    return pre_s, "S_REGENERATION_FAILED_FALLBACK", reason


def apply_s_fallback(trace, response, *, expected_model, verified=False):
    """Apply a shared failed response to this arm's own pre-S answer."""
    pre_s = trace["pre_s_answer"]
    answer, state, reason = select_s_answer(pre_s, response, expected_model=expected_model, verified=verified,
                                             s_triggered=trace.get("s_trigger", False))
    return {"sample_id": trace["sample_id"], "arm_id": trace["arm_id"],
            "s_triggered": bool(trace.get("s_trigger", False)), "pre_s_answer": pre_s,
            "failed_request_key": trace.get("failed_request_key"),
            "fallback_reason": reason, "final_answer": answer,
            "cost_provenance": trace.get("cost_provenance"),
            "protocol_version": PROTOCOL_VERSION, "decision_state": state}
