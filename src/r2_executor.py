"""Selected definitions from the frozen research implementation."""

from __future__ import annotations

import re

import string

ARMS = {
    "B0": (False, False, False), "B1": (True, False, False),
    "B2": (False, True, False), "B3": (False, False, True),
    "B4": (True, True, False), "B5": (True, False, True),
    "B6": (False, True, True), "B7": (True, True, True),
}

YES_NO = {"am", "are", "can", "could", "did", "do", "does", "had", "has", "have",
          "is", "should", "was", "were", "will", "would"}

SAMPLE_FIELDS = ("sample_id", "question", "context", "y0")

def normalize(text):
    text = "".join(ch.lower() for ch in (text or "") if ch not in string.punctuation)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())

def lexical_trigger(question, answer, context):
    tokens = normalize(question).split()
    answer = normalize(answer)
    return bool(tokens and tokens[0] not in YES_NO and answer and answer not in normalize(context))
