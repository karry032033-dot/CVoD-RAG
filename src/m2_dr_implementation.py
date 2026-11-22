"""Frozen pure routing and prompt logic for M2-DR. No model calls or scoring."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent
DISCRIMINATOR_PROMPT = ROOT / "m2_dr_discriminator_prompt.txt"
RESOLVE_PROMPT = ROOT / "m2_dr_resolve_prompt.txt"


def render_discriminator(question, current_answer):
    return (
        DISCRIMINATOR_PROMPT.read_text(encoding="utf-8")
        .replace("{{QUESTION}}", question)
        .replace("{{CURRENT_ANSWER}}", current_answer)
    )


def render_resolve(question, context):
    return (
        RESOLVE_PROMPT.read_text(encoding="utf-8")
        .replace("{{QUESTION}}", question)
        .replace("{{CONTEXT}}", context)
    )


def action(discriminator_output):
    """Invalid output fails closed to the frozen T1 answer."""
    return "RE_SOLVE" if discriminator_output.strip() == "OFF_TOPIC" else "RETAIN_T1"


if __name__ == "__main__":
    assert action("OFF_TOPIC") == "RE_SOLVE"
    assert action("OK") == "RETAIN_T1"
    assert action("OFF_TOPIC because") == "RETAIN_T1"
    print("M2-DR-IMPLEMENTATION-SELF-CHECK-PASS")
