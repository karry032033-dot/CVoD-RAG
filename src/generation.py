"""Selected definitions from the frozen research implementation."""

def build_prompt(question, context, prompt_style="concise_grounded", model_name=None):
    prefix = ""
    if model_name and model_name.lower().startswith("qwen3"):
        # Qwen3 models in Ollama may spend short generations on hidden/visible
        # reasoning unless no-think mode is requested. For answer-only QA
        # experiments, concise direct output is easier to evaluate.
        prefix = "/no_think\n"
    if prompt_style == "concise_grounded":
        if context:
            return prefix + (
                "Answer the question using only the provided context. "
                "Give the shortest answer that is fully supported by the context. "
                "Do not explain.\n\n"
                "Context:\n%s\n\nQuestion: %s\nAnswer:" % (context, question)
            )
        return prefix + (
            "Answer the question as concisely as possible. Do not explain.\n\n"
            "Question: %s\nAnswer:" % question
        )
    if prompt_style == "structured_multihop":
        return prefix + (
            "Use only the provided context.\n\n"
            "This is a multi-hop question. Before answering, determine which facts in the\n"
            "context connect the entities or events needed to answer the question, and make\n"
            "sure the final answer is supported by the complete chain of relevant facts.\n\n"
            "Return only the shortest final answer.\n"
            "Do not explain your reasoning.\n\n"
            "Context:\n%s\n\n"
            "Question:\n%s\n\n"
            "Answer:" % (context, question)
        )
    raise ValueError("Unsupported prompt_style: %s" % prompt_style)
