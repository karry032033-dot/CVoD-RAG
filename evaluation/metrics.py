"""Selected definitions from the frozen research implementation."""

import re

import string

from collections import Counter

ARTICLES = re.compile(r"\b(a|an|the)\b", re.UNICODE)

def normalize_answer(s):
    def lower(text):
        return text.lower()

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def remove_articles(text):
        return ARTICLES.sub(" ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    return white_space_fix(remove_articles(remove_punc(lower(s or ""))))

def answer_precision_recall(prediction, gold):
    pred_tokens = normalize_answer(prediction).split()
    gold_tokens = normalize_answer(gold).split()
    if not pred_tokens and not gold_tokens:
        return 1.0, 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0, 0.0
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_same = sum(common.values())
    return num_same / len(pred_tokens), num_same / len(gold_tokens)

def official_answer_metrics(prediction, gold):
    """Apply the answer-scoring rules from the official HotpotQA evaluator."""
    normalized_prediction = normalize_answer(prediction)
    normalized_gold = normalize_answer(gold)
    exact = float(normalized_prediction == normalized_gold)
    special_answers = {"yes", "no", "noanswer"}
    if (
        normalized_prediction in special_answers
        or normalized_gold in special_answers
    ) and normalized_prediction != normalized_gold:
        return {
            "official_answer_em": exact,
            "official_answer_f1": 0.0,
            "official_answer_precision": 0.0,
            "official_answer_recall": 0.0,
        }

    precision, recall = answer_precision_recall(prediction, gold)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "official_answer_em": exact,
        "official_answer_f1": f1,
        "official_answer_precision": precision,
        "official_answer_recall": recall,
    }
