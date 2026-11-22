"""Build complete prospective request identities from the frozen JSON protocol."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_protocol(path=HERE / "R2_PROTOCOL.json"):
    raw = Path(path).read_bytes()
    p = json.loads(raw)
    template = p["template"].encode("utf-8")
    if hashlib.sha256(template).hexdigest() != p["template_sha256"]:
        raise ValueError("inline Ollama template hash mismatch")
    return p, hashlib.sha256(raw).hexdigest()


def request_factory(protocol):
    def build(action, sample, previous_answer=None):
        cfg = protocol["actions"][action]
        values = {"question": sample["question"], "context": sample["context"],
                  "previous_answer": previous_answer or ""}
        prompt = cfg["prompt"].format(**values)
        options = dict(protocol["ollama_defaults_explicit"])
        options.update({k: cfg[k] for k in ("temperature", "top_p", "top_k", "seed", "num_predict", "num_ctx")})
        return {"action": action, "sample_id": sample["sample_id"], "question": sample["question"],
                "context": sample["context"], "system": protocol["body"]["system"], "prompt": prompt,
                "model": protocol["model"], "digest": protocol["model_digest"],
                "quantization": protocol["quantization"], "think": cfg["think"], "options": options,
                "backend": f"ollama-{protocol['target_ollama_version']}", "template": protocol["template"],
                "num_ctx": options["num_ctx"], "extractor": "clean_answer-v1",
                "timeouts_seconds": {"connect": protocol["timeouts_seconds"]["connect"],
                    "read": protocol["timeouts_seconds"]["read"][action]},
                "previous_answer": previous_answer, "raw": protocol["body"]["raw"],
                "truncate": protocol["body"]["truncate"], "shift": protocol["body"]["shift"],
                "realization_id": f"{action}:{sample['sample_id']}"}
    return build
