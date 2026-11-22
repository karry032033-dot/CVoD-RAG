"""Synthetic fixture for the frozen L/S/T policy. No model calls or research data."""

from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "evaluation")]
from generation import build_prompt
from paired_outcomes import decompose
from r2_adapter import clean_answer, ollama_payload, parse_response
from r2_executor import lexical_trigger
from r2_requests import load_protocol, request_factory
from r5_executor import execute, execute_arm
from paired_stats import paired_difference


def main():
    question = "Which color is on the flag?"
    evidence = "SYNTHETIC: The flag is red. The circle is green."
    protocol = json.loads((ROOT / "configs/R2_PROTOCOL.json").read_bytes())
    protocol["template"] = "synthetic CPU fixture"
    with tempfile.TemporaryDirectory() as tmp:
        config = Path(tmp) / "protocol.json"
        config.write_text(json.dumps(protocol), encoding="utf-8")
        try:
            load_protocol(config)
        except ValueError as exc:
            assert "template hash mismatch" in str(exc)
        else:
            raise AssertionError("Unverified fixture template was accepted")
        protocol["template_sha256"] = sha256(protocol["template"].encode()).hexdigest()
        config.write_text(json.dumps(protocol), encoding="utf-8")
        protocol, _ = load_protocol(config)
    factory = request_factory(protocol)
    prompt = build_prompt(question, evidence, model_name=protocol["model"])
    assert prompt.startswith("/no_think") and question in prompt and evidence in prompt
    initial_answers = ["red", "red", "blue"]
    assert lexical_trigger(question, "blue", evidence)
    assert not lexical_trigger("Is the flag blue?", "blue", evidence)
    assert not lexical_trigger(question, "", evidence)
    assert not lexical_trigger(question, "RED.", evidence)
    assert not lexical_trigger("", "blue", evidence)
    calls = []

    def run(y0, decision, outcome="valid", verified=True, arm="B7"):
        sample = {"sample_id": "synthetic-flag", "question": question, "context": evidence,
                  "y0": y0, "gold": "SYNTHETIC OFFLINE ONLY"}
        calls.clear()

        def invoke(req):
            action = req["action"]
            calls.append(action)
            assert req["context"] == evidence and req["question"] == question
            payload = ollama_payload(req)
            assert "SYNTHETIC OFFLINE ONLY" not in json.dumps(payload)
            assert payload["options"]["num_ctx"] == 4096
            if action == "D":
                assert evidence not in payload["prompt"]
                assert question in payload["prompt"] and req["previous_answer"] in payload["prompt"]
                response, reason = decision, "stop"
            else:
                assert evidence in payload["prompt"] and question in payload["prompt"]
                assert req["previous_answer"] is None
                response, reason = {"valid": ("green", "stop"), "empty": ("", "stop"),
                                    "truncated": ("unfinished", "length")}[outcome]
            raw = json.dumps({"model": req["model"], "done": True, "done_reason": reason,
                              "response": response, "prompt_eval_count": 12, "eval_count": 2})
            res = parse_response({"status": 200, "raw": raw, "elapsed_seconds": .2}, req["model"])
            if res["state"] == "SUCCESS":
                res["answer"] = clean_answer(res["answer"])
            res["r5_provenance_verified"] = verified
            return res

        return execute_arm(sample, invoke, factory, arm, decisions=[])

    start = run(initial_answers[0], "OK")
    assert calls == ["D", "T"] and start["answer"] == "green" and start["logical_t_module_attempted"]
    non_exact = run(initial_answers[0], "OFF_TOPIC because")
    assert calls == ["D", "T"] and not non_exact["s_trigger"]
    semantic = run(initial_answers[1], "OFF_TOPIC")
    assert calls == ["D", "R"] and semantic["s_trigger"] and not semantic["logical_t_module_attempted"]
    lexical = run(initial_answers[2], "OK")
    assert calls == ["T", "D"] and lexical["l_trigger"] and lexical["actual_t_stages"] == ["L_candidate"]
    for outcome in ("empty", "truncated"):
        assert run("red", "OK", outcome)["answer"] == "red"
        assert run("red", "OFF_TOPIC", outcome)["answer"] == "red"
        try:
            run("red", "OK", outcome, verified=False)
        except RuntimeError:
            pass
        else:
            raise AssertionError("Unverified fallback was accepted")
    try:
        execute([{"sample_id": "synthetic-duplicate"}] * 2, None, factory)
    except ValueError as exc:
        assert "duplicate sample IDs" in str(exc)
    else:
        raise AssertionError("Duplicate IDs were accepted")

    rows = [{"example_id": id_, "condition_label": arm, "answer_f1": score}
            for arm, values in (("post", (("a", .5), ("b", .75))), ("pre", (("b", 1), ("a", 0))))
            for id_, score in values]
    aligned = paired_difference(rows, "post", "pre", "answer_f1", 1000, 77)
    parts = decompose([.5, -.25])
    assert aligned["n"] == parts["n"] == 2 and aligned["mean_difference"] == parts["net"] == .125
    assert parts["benefit"] == .25 and parts["loss"] == .125
    print("SYNTHETIC PASS: fixed evidence, initial prompt, L/S/T paths, G1 fallback, paired IDs and benefit/loss.")


if __name__ == "__main__":
    main()
