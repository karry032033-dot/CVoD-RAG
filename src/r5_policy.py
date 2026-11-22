"""P2-R5 T failure fallback decision; never sends or retries requests."""
import json
import hashlib

from r2_adapter import clean_answer

PROTOCOL_VERSION = "P2-R5-BOUNDED-ST-FALLBACK-v1"


def select_t_answer(pre_t, response, *, expected_model, verified, attempted=True):
    if not attempted:
        return pre_t, "NOT_ATTEMPTED", None
    if not verified or response.get("state") not in ("SUCCESS", "FAILED", "TRUNCATED"):
        raise RuntimeError("T result provenance/state is not eligible for fallback")
    raw = response.get("raw")
    try:
        data = json.loads(raw) if isinstance(raw, str) else None
    except (ValueError, TypeError):
        data = None
    if (response.get("http_status") != 200 or not isinstance(data, dict)
            or data.get("model") != expected_model or data.get("done") is not True
            or data.get("done_reason") not in ("stop", "length")
            or not isinstance(data.get("response"), str)):
        raise RuntimeError("T result is not a verified completed target-model response")
    parsed_answer = clean_answer(data["response"])
    expected_state = "TRUNCATED" if data["done_reason"] == "length" else ("SUCCESS" if parsed_answer else "FAILED")
    if response.get("state") != expected_state:
        raise RuntimeError("T response state conflicts with its raw completed response")
    if data["done_reason"] == "length":
        return pre_t, "T_GENERATION_FAILED_FALLBACK", "done_reason_length"
    answer = parsed_answer
    if not answer:
        return pre_t, "T_GENERATION_FAILED_FALLBACK", "empty_extracted_answer"
    return answer, "SUCCESS", None


def apply_t_fallback(*, sample_id, arm_id, stage, pre_t_answer, request_key,
                     response, expected_model, verified, logical_t_module_attempted):
    answer, state, reason = select_t_answer(pre_t_answer, response,
        expected_model=expected_model, verified=verified)
    raw = response.get("raw", "")
    parsed = json.loads(raw)
    raw_answer = parsed.get("response", "")
    empty_final = not clean_answer(raw_answer)
    truncated = parsed.get("done_reason") == "length"
    return {"sample_id": sample_id, "arm_id": arm_id, "stage": stage,
        "physical_t_candidate_attempted": True,
        "logical_t_module_attempted": bool(logical_t_module_attempted),
        "t_attempted": True, "t_successful": state == "SUCCESS",
        "t_truncated": truncated,
        "t_empty_final_answer": empty_final,
        "t_fallback_applied": state == "T_GENERATION_FAILED_FALLBACK",
        "pre_t_answer": pre_t_answer, "final_selected_answer": answer,
        "request_key": request_key,
        "raw_response_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "prompt_tokens": response.get("prompt_tokens"),
        "generated_tokens": response.get("generated_tokens"),
        "elapsed_seconds": response.get("elapsed_seconds"),
        "fallback_reason": reason, "decision_state": state,
        "protocol_version": PROTOCOL_VERSION}
