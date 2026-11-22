"""Selected definitions from the frozen research implementation."""

from __future__ import annotations

import hashlib

import json

UNKNOWN = {"unknown": True}

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)

def identity(request):
    required = ("action", "sample_id", "question", "context", "system", "prompt", "model", "digest",
                "quantization", "think", "options", "backend", "template", "num_ctx", "extractor", "timeouts_seconds")
    spec = {k: request.get(k, UNKNOWN) for k in required}
    spec["previous_answer"] = request.get("previous_answer", UNKNOWN)
    for k in ("raw", "truncate", "shift", "realization_id"):
        spec[k] = request.get(k, UNKNOWN)
    encoded = canonical(spec).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest(), spec

def cache_eligible(spec):
    """Unknown historical settings are never evidence of matching identity."""
    def complete(v):
        if isinstance(v, dict):
            return v != UNKNOWN and all(complete(x) for x in v.values())
        if isinstance(v, list):
            return all(complete(x) for x in v)
        return isinstance(v, (str, int, float, bool)) or v is None
    return all(k == "previous_answer" or spec.get(k) is not None for k in spec) and complete(spec)

def ollama_payload(request):
    if not cache_eligible(identity(request)[1]):
        raise ValueError("request identity has unknown fields")
    opts = request["options"]
    if not isinstance(opts, dict):
        raise ValueError("options must be an object")
    opts = dict(opts)
    if request["num_ctx"] != opts.get("num_ctx"):
        raise ValueError("num_ctx identity must match explicit Ollama options")
    supported = {"temperature", "top_p", "top_k", "typical_p", "num_predict", "num_ctx", "seed", "stop",
                 "repeat_penalty", "repeat_last_n", "presence_penalty", "frequency_penalty",
                 "num_keep", "num_batch", "draft_num_predict", "num_thread", "num_gpu"}
    unsupported = set(opts) - supported
    if unsupported:
        raise ValueError(f"unsupported Ollama options: {sorted(unsupported)}")
    return {"model": request["model"], "prompt": request["prompt"], "system": request["system"],
            "stream": False, "think": request["think"], "raw": request["raw"],
            "template": request["template"], "truncate": request["truncate"],
            "shift": request["shift"], "options": opts}

def clean_answer(text):
    """Frozen pure logic copied from generation.clean_answer (same extraction version)."""
    text = (text or "").strip()
    if not text:
        return ""
    for prefix in ["Answer:", "Final answer:", "The answer is"]:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[0] if lines else ""

def parse_response(response, expected_model):
    base = {"http_status": response.get("status"), "raw": response.get("raw"),
            "elapsed_seconds": response.get("elapsed_seconds")}
    if response.get("status") != 200:
        return {**base, "state": "FAILED", "reason": "http_status"}
    try:
        data = json.loads(response["raw"])
    except (ValueError, TypeError):
        return {**base, "state": "FAILED", "reason": "invalid_json"}
    if not isinstance(data, dict) or not isinstance(data.get("response"), str):
        return {**base, "state": "FAILED", "reason": "missing_response"}
    answer = data["response"]
    done = data.get("done_reason")
    if data.get("model") != expected_model:
        state = "FAILED"
    elif data.get("done") is not True or done not in ("stop", "length"):
        state = "FAILED"
    elif done == "length":
        state = "TRUNCATED"
    elif not answer.strip():
        state = "FAILED"
    else:
        state = "SUCCESS"
    return {**base, "state": state, "answer": answer, "response_text": answer,
            "done_reason": done, "prompt_tokens": data.get("prompt_eval_count"),
            "generated_tokens": data.get("eval_count"), "metadata": data,
            "reason": "model_mismatch" if data.get("model") != expected_model else None}
